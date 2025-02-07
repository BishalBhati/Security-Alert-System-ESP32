import argparse
import hashlib
import logging
import random
import socket
import sys
import time

RESPONSE_OK = 0
RESPONSE_REQUEST_AUTH = 1

RESPONSE_HEADER_OK = 64
RESPONSE_AUTH_OK = 65
RESPONSE_UPDATE_PREPARE_OK = 66
RESPONSE_BIN_MD5_OK = 67
RESPONSE_RECEIVE_OK = 68
RESPONSE_UPDATE_END_OK = 69

RESPONSE_ERROR_MAGIC = 128
RESPONSE_ERROR_UPDATE_PREPARE = 129
RESPONSE_ERROR_AUTH_INVALID = 130
RESPONSE_ERROR_WRITING_FLASH = 131
RESPONSE_ERROR_UPDATE_END = 132
RESPONSE_ERROR_INVALID_BOOTSTRAPPING = 133
RESPONSE_ERROR_WRONG_CURRENT_FLASH_CONFIG = 134
RESPONSE_ERROR_WRONG_NEW_FLASH_CONFIG = 135
RESPONSE_ERROR_ESP8266_NOT_ENOUGH_SPACE = 136
RESPONSE_ERROR_ESP32_NOT_ENOUGH_SPACE = 137
RESPONSE_ERROR_UNKNOWN = 255

OTA_VERSION_1_0 = 1

MAGIC_BYTES = [0x6C, 0x26, 0xF7, 0x5C, 0x45]

_LOGGER = logging.getLogger(__name__)

def is_ip_address(host):
    parts = host.split('.')
    if len(parts) != 4:
        return False
    try:
        for p in parts:
            int(p)
        return True
    except ValueError:
        return False

def _resolve_with_zeroconf(host):
    try:
        zc = Zeroconf()
    except Exception as err:
        raise CustomError("Cannot start mDNS sockets, is this a docker container without "
                           "host network mode?") from err
    try:
        info = zc.resolve_host(host + '.')
    except Exception as err:
        raise CustomError(f"Error resolving mDNS hostname: {err}") from err
    finally:
        zc.close()
    if info is None:
        raise CustomError("Error resolving address with mDNS: Did not respond. "
                           "Maybe the device is offline.")
    return info

def resolve_ip_address(host):
    errs = []

    ## TODO: can be resolved installing zeroconf via pip3
    # if host.endswith('.local'):
    #     try:
    #         return _resolve_with_zeroconf(host)
    #     except CustomError as err:
    #         errs.append(str(err))

    try:
        return socket.gethostbyname(host)
    except OSError as err:
        errs.append(str(err))
        raise CustomError("Error resolving IP address: {}"
                           "".format(', '.join(errs))) from err

class CustomError(Exception):
    """General exception occurred."""

class ProgressBar:
    def __init__(self):
        self.last_progress = None

    def update(self, progress):
        bar_length = 60
        status = ""
        if progress >= 1:
            progress = 1
            status = "Done...\r\n"
        new_progress = int(progress * 100)
        if new_progress == self.last_progress:
            return
        self.last_progress = new_progress
        block = int(round(bar_length * progress))
        text = "\rUploading: [{0}] {1}% {2}".format("=" * block + " " * (bar_length - block),
                                                    new_progress, status)
        sys.stderr.write(text)
        sys.stderr.flush()

    # pylint: disable=no-self-use
    def done(self):
        sys.stderr.write('\n')
        sys.stderr.flush()


class OTAError(CustomError):
    pass

def parse_args(argv):
    parser = argparse.ArgumentParser(description=f'espota-2smart v1')
    parser.add_argument('-H', '--host',
        help="host of esp device, (cloud be IP address or local domain)")
    parser.add_argument('-P', '--port',
        help="path to file of binary firmware build (usually is located in .pioenvs/firmare_name/firmware.bin)",
        type=int,
        default=3232)
    parser.add_argument('-p', '--password',
        help="password to connect esp device over the air")
    parser.add_argument('-f', '--filename',
        help="path to file of binary firmware build (usually is located in .pioenvs/firmare_name/firmware.bin)")

    return parser.parse_args(argv[1:])

def recv_decode(sock, amount, decode=True):
    data = sock.recv(amount)
    if not decode:
        return data
    return list(data)


def receive_exactly(sock, amount, msg, expect, decode=True):
    if decode:
        data = []
    else:
        data = b''

    try:
        data += recv_decode(sock, 1, decode=decode)
    except OSError as err:
        raise OTAError(f"Error receiving acknowledge {msg}: {err}") from err

    try:
        check_error(data, expect)
    except OTAError as err:
        sock.close()
        raise OTAError(f"Error {msg}: {err}") from err

    while len(data) < amount:
        try:
            data += recv_decode(sock, amount - len(data), decode=decode)
        except OSError as err:
            raise OTAError(f"Error receiving {msg}: {err}") from err
    return data


def check_error(data, expect):
    if not expect:
        return
    dat = data[0]
    if dat == RESPONSE_ERROR_MAGIC:
        raise OTAError("Error: Invalid magic byte")
    if dat == RESPONSE_ERROR_UPDATE_PREPARE:
        raise OTAError("Error: Couldn't prepare flash memory for update. Is the binary too big? "
                       "Please try restarting the ESP.")
    if dat == RESPONSE_ERROR_AUTH_INVALID:
        raise OTAError("Error: Authentication invalid. Is the password correct?")
    if dat == RESPONSE_ERROR_WRITING_FLASH:
        raise OTAError("Error: Wring OTA data to flash memory failed. See USB logs for more "
                       "information.")
    if dat == RESPONSE_ERROR_UPDATE_END:
        raise OTAError("Error: Finishing update failed. See the MQTT/USB logs for more "
                       "information.")
    if dat == RESPONSE_ERROR_INVALID_BOOTSTRAPPING:
        raise OTAError("Error: Please press the reset button on the ESP. A manual reset is "
                       "required on the first OTA-Update after flashing via USB.")
    if dat == RESPONSE_ERROR_WRONG_CURRENT_FLASH_CONFIG:
        raise OTAError("Error: ESP has been flashed with wrong flash size. Please choose the "
                       "correct 'board' option (esp01_1m always works) and then flash over USB.")
    if dat == RESPONSE_ERROR_WRONG_NEW_FLASH_CONFIG:
        raise OTAError("Error: ESP does not have the requested flash size (wrong board). Please "
                       "choose the correct 'board' option (esp01_1m always works) and try "
                       "uploading again.")
    if dat == RESPONSE_ERROR_ESP8266_NOT_ENOUGH_SPACE:
        raise OTAError("Error: ESP does not have enough space to store OTA file. Please try "
                       "flashing a minimal firmware (remove everything except ota)")
    if dat == RESPONSE_ERROR_ESP32_NOT_ENOUGH_SPACE:
        raise OTAError("Error: The OTA partition on the ESP is too small. ESPHome needs to resize "
                       "this partition, please flash over USB.")
    if dat == RESPONSE_ERROR_UNKNOWN:
        raise OTAError("Unknown error from ESP")
    if not isinstance(expect, (list, tuple)):
        expect = [expect]
    if dat not in expect:
        raise OTAError("Unexpected response from ESP: 0x{:02X}".format(data[0]))


def send_check(sock, data, msg):
    try:
        if isinstance(data, (list, tuple)):
            data = bytes(data)
        elif isinstance(data, int):
            data = bytes([data])
        elif isinstance(data, str):
            data = data.encode('utf8')

        sock.sendall(data)
    except OSError as err:
        raise OTAError(f"Error sending {msg}: {err}") from err


def perform_ota(sock, password, file_handle, filename):
    file_md5 = hashlib.md5(file_handle.read()).hexdigest()
    file_size = file_handle.tell()
    _LOGGER.info('Uploading %s (%s bytes)', filename, file_size)
    file_handle.seek(0)
    _LOGGER.debug("MD5 of binary is %s", file_md5)

    # Enable nodelay, we need it for phase 1
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    send_check(sock, MAGIC_BYTES, 'magic bytes')

    _, version = receive_exactly(sock, 2, 'version', RESPONSE_OK)
    if version != OTA_VERSION_1_0:
        raise OTAError(f"Unsupported OTA version {version}")

    # Features
    send_check(sock, 0x00, 'features')
    receive_exactly(sock, 1, 'features', RESPONSE_HEADER_OK)

    auth, = receive_exactly(sock, 1, 'auth', [RESPONSE_REQUEST_AUTH, RESPONSE_AUTH_OK])
    if auth == RESPONSE_REQUEST_AUTH:
        if not password:
            raise OTAError("ESP requests password, but no password given!")
        nonce = receive_exactly(sock, 32, 'authentication nonce', [], decode=False).decode()
        _LOGGER.debug("Auth: Nonce is %s", nonce)
        cnonce = hashlib.md5(str(random.random()).encode()).hexdigest()
        _LOGGER.debug("Auth: CNonce is %s", cnonce)

        send_check(sock, cnonce, 'auth cnonce')

        result_md5 = hashlib.md5()
        result_md5.update(password.encode('utf-8'))
        result_md5.update(nonce.encode())
        result_md5.update(cnonce.encode())
        result = result_md5.hexdigest()
        _LOGGER.debug("Auth: Result is %s", result)

        send_check(sock, result, 'auth result')
        receive_exactly(sock, 1, 'auth result', RESPONSE_AUTH_OK)

    file_size_encoded = [
        (file_size >> 24) & 0xFF,
        (file_size >> 16) & 0xFF,
        (file_size >> 8) & 0xFF,
        (file_size >> 0) & 0xFF,
    ]
    send_check(sock, file_size_encoded, 'binary size')
    receive_exactly(sock, 1, 'binary size', RESPONSE_UPDATE_PREPARE_OK)

    send_check(sock, file_md5, 'file checksum')
    receive_exactly(sock, 1, 'file checksum', RESPONSE_BIN_MD5_OK)

    # Disable nodelay for transfer
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 0)
    # Limit send buffer (usually around 100kB) in order to have progress bar
    # show the actual progress
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8192)
    # Set higher timeout during upload
    sock.settimeout(20.0)

    offset = 0
    progress = ProgressBar()
    while True:
        chunk = file_handle.read(1024)
        if not chunk:
            break
        offset += len(chunk)

        try:
            sock.sendall(chunk)
        except OSError as err:
            sys.stderr.write('\n')
            raise OTAError(f"Error sending data: {err}") from err

        progress.update(offset / float(file_size))
    progress.done()

    # Enable nodelay for last checks
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    _LOGGER.info("Waiting for result...")

    receive_exactly(sock, 1, 'receive OK', RESPONSE_RECEIVE_OK)
    receive_exactly(sock, 1, 'Update end', RESPONSE_UPDATE_END_OK)
    send_check(sock, RESPONSE_OK, 'end acknowledgement')

    _LOGGER.info("OTA successful")

    # Do not connect logs until it is fully on
    time.sleep(1)


def run_ota_impl_(args):
    remote_host = args.host
    remote_port = args.port
    password = args.password
    filename = args.filename
    if is_ip_address(remote_host):
        _LOGGER.info("Connecting to %s", remote_host)
        ip = remote_host
    else:
        _LOGGER.info("Resolving IP address of %s", remote_host)
        try:
            ip = resolve_ip_address(remote_host)
        except CustomError as err:
            _LOGGER.error("Error resolving IP address of %s. Is it connected to WiFi?",
                          remote_host)
            _LOGGER.error("(If this error persists, please set a static IP address: "
                          "https://esphome.io/components/wifi.html#manual-ips)")
            raise OTAError(err) from err
        _LOGGER.info(" -> %s", ip)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10.0)
    try:
        sock.connect((ip, remote_port))
    except OSError as err:
        sock.close()
        _LOGGER.error("Connecting to %s:%s failed: %s", remote_host, remote_port, err)
        return 1

    file_handle = open(filename, 'rb')
    try:
        perform_ota(sock, password, file_handle, filename)
    except OTAError as err:
        _LOGGER.error(str(err))
        return 1
    finally:
        sock.close()
        file_handle.close()

    return 0


def run_ota(argv):
    args = parse_args(argv)
    try:
        return run_ota_impl_(args)
    except OTAError as err:
        _LOGGER.error(err)
        return 1

def main():
    try:
        return run_ota(sys.argv)
    except CustomError as e:
        _LOGGER.error(e)
        return 1
    except KeyboardInterrupt:
        return 1


if __name__ == "__main__":
    sys.exit(main())
