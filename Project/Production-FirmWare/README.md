# How to write ESPHome firmware to device (production)

## Description

This is archive with production firmware.
It doesn't contain `.yml` config file and you cannot modify firmware in this archive.
If you want to modify current firmware, please go back to `test` environment.

## Prerequirements

1. Need have `python` (>= v3) or `docker` installed.

2. Have connected device to your computer.

3. Device should be listed in /dev as one of this:

    ```
    (Linux)
    /dev/ttyUSB0

    (OSX)
    /dev/cu.SLAB_USBtoUART
    /dev/cu.usbserial-0001
    ```

In Linux you need to change file permissions to flash a device
```bash
    chown $USER:$USER /dev/ttyUSB0
```

## Python

Install required packages to use `2smart.sh` script
```bash
    pip3 install -r requirements.txt
```

## Docker

To use `2smart_docker.sh` you need to pull required images:
- esptool [docker image](https://hub.docker.com/r/2smartdev/esptool)

## Erase device

Do not forget to erase device before writing firmware.
To erase device you need hold boot button and run command
```bash
    ./2smart.sh erase_flash
    # example
    # ./2smart.sh erase_flash
```
or with `docker` (Linux only)
```bash
    ./2smart_docker.sh erase_flash
    # example
    # ./2smart_docker.sh erase_flash
```

## Write firmware with assembled binaries via docker (Linux only)

1. Open folder after unzipping downloaded archive in terminal:
```bash
    cd <unzipped_archive>
    ls .
    # 2smart.sh              2smart_docker.sh       2smartota.py           README.md              boot_app0.bin          bootloader_dio_40m.bin              esptool.py             firmware.bin           partitions.bin
```

2. Use `2smart_docker.sh` to flash a device with compiled firmware
```bash
    ./2smart_docker.sh write --device <DEVICE>
    # example
    # ./2smart_docker.sh write --device /dev/ttyUSB0
```

3. When process completed turn off and on device again.

4. If everything is okay it should start AP (WiFi access point) with product name.

## Writing firmware with assembled binaries via installed esphome tool locally (Linux/OSX)

1. Open folder after unzipping downloaded archive in terminal (there should be config file .yml and folder with build):
```bash
    cd <unzipped_archive>
    ls .
    # 2smart.sh              2smart_docker.sh       2smartota.py           README.md              boot_app0.bin          bootloader_dio_40m.bin              esptool.py             firmware.bin           partitions.bin
```

2. Use `2smart.sh` script to upload build
```bash
    ./2smart.sh write --device <DEVICE>
    # example
    # ./2smart.sh write --device /dev/ttyUSB0
```

3. When process completed turn off and on device again.

4. If everything is okay it should start AP (WiFi access point) with product name.

## Debug

If AP is not appearing in WiFi list or device is not working the right way, you can inspect device's logs
```bash
    ./2smart.sh logs --device <DEVICE>
    # example
    # ./2smart.sh logs --device /dev/ttyUSB0
```
or with `docker` (Linux only)
```bash
    ./2smart_docker.sh logs --device <DEVICE>
    # example
    # ./2smart_docker.sh logs --device /dev/ttyUSB0
```

## OTA update

### Prerequirements

A device flashed with ESPHome firmware from 2Smart Cloud with enabled [ota component](https://esphome.io/components/ota.html?highlight=ota). Configuration [example](https://github.com/2SmartCloud/2smart-cloud-esphome/blob/master/examples/blinker_with_ota.yml).

### Why it may be needed

It may be usefull, if your device is already mounted or it's hard to re-flash it by tty.

### Commands

- can be used simplified command with work Over the Air (OTA) if esphome is installed locally (Linux/OSX):
    ```bash
    ./2smart.sh write_ota \
        --host <HOST> \
        --port <PORT> \
        --pass <PASSWORD>
    ```
    >  \<HOST\> - Should be IP address
    >  \<PORT\> - Optional Default is 3232
- with docker:
    ```bash
    ./2smart_docker.sh write_ota \
        --host <HOST> \
        --port <PORT> \
        --pass <PASSWORD>
    ```
    >  \<HOST\> - Should be IP address
    >  \<PORT\> - Optional Default is 3232

## Useful links

1. [2Smart Cloud ESPHome documentation](https://github.com/2SmartCloud/2smart-cloud-esphome)
2. [Official ESPHome documentation](https://esphome.io/)
3. [How to create a Wi-Fi switch to control via a mobile app and Telegram bot](https://2smart.com/blog/tpost/2n6ankych1-how-to-create-a-wi-fi-switch-to-control)
