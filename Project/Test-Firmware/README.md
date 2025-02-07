# How to write ESPHome firmware to device (test)

## Description

This is archive with test firmware.
It contains `device1702611907531972.yml` config file and you can modify firmware in this archive.
Take a look at [Local development](#local-development) step if you want to modify `device1702611907531972.yml` config file.
Don't forget to update config at 2Smart Cloud platform, if there was any changes in `device1702611907531972.yml` file.

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
- ESPHome [docker image](https://hub.docker.com/r/2smartdev/esphome)
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

1. Open folder after unzipping downloaded archive in terminal (there should be config file .yml and folder with build):

    ```bash
    cd <unzipped_archive>
    ls .
    # 2smart.sh              2smart_docker.sh       2smartota.py           README.md              boot_app0.bin          bootloader_dio_40m.bin              device1702611907531972.yml              esptool.py             firmware.bin           partitions.bin
    ```

2. Use `2smart_docker.sh` to flash a device with compiled firmware
```bash
    ./2smart_docker.sh write --device <DEVICE>
    # example
    # ./2smart_docker.sh write --device /dev/ttyUSB0
```

3. When process completed turn off and on device again.

4. If everything is okay it should appear in web-interface and mobile app.

## Writing firmware with assembled binaries via installed esphome tool locally (Linux/OSX)

1. Open folder after unzipping downloaded archive in terminal (there should be config file .yml and folder with build):

    ```bash
    cd <unzipped_archive>
    ls .
    # 2smart.sh              2smart_docker.sh       2smartota.py           README.md              boot_app0.bin          bootloader_dio_40m.bin              device1702611907531972.yml              esptool.py             firmware.bin           partitions.bin
    ```

2. Use `2smart.sh` script to upload build
```bash
    ./2smart.sh write --device <DEVICE>
    # example
    # ./2smart.sh write --device /dev/ttyUSB0
```

3. When process completed turn off and on device again.

4. If everything is okay it should appear in web-interface and mobile app

## Debug

If device is not working the right way, you can inspect device's logs
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

It may be useful, if your device is already mounted or it's hard to re-flash it by tty.

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

## Local development

### Prerequirements

You need have device connected and `device1702611907531972.yml` file changed after updates.

### Why it may be needed

It may be usefull, if you are testing your firmware configuration and making lot of changes to `.yml` file.
It's much faster to compile new firmware with changes locally.

### Commands

#### With ESPHome docker image (OSX/Windows)

1. Open folder after unzipping downloaded archive in terminal (there should be config file `.yml` and folder with build):

    ```bash
    $ cd <unzipped_archive>
    $ ls -la .
    total 2136
    drwx------@ 12 user  group     384 Mar 15 12:52 .
    drwx------@ 34 user  group    1088 Mar 15 12:52 ..
    -rwxr-xr-x@  1 user  group    3684 Mar 15 10:51 2smart.sh
    -rwxr-xr-x@  1 user  group    4228 Mar 15 10:51 2smart_docker.sh
    -rw-r--r--@  1 user  group   12248 Mar 15 10:51 2smartota.py
    -rw-r--r--@  1 user  group    4145 Mar 15 10:51 README.md
    -rw-r--r--@  1 user  group    8192 Mar 15 10:51 boot_app0.bin
    -rw-r--r--@  1 user  group   15872 Mar 15 10:51 bootloader_dio_40m.bin
    -rw-r--r--@  1 user  group     704 Mar 15 10:51 device1702611907531972.yml
    -rw-r--r--@  1 user  group  143640 Mar 15 10:51 esptool.py
    -rw-r--r--@  1 user  group  876992 Mar 15 10:51 firmware.bin
    -rw-r--r--@  1 user  group    3072 Mar 15 10:51 partitions.bin
    ```
2. Use esphome command inside docker container to compile (our helper script will simplify this):
```bash
    ./2smart_docker.sh esphome_compile --id device1702611907531972
```

3. Copy binaries:
```bash
    ./2smart_docker.sh copy --product 1702611907531972
```

4. Upload compiled binaries to device: (binary upload with docker image is not supported in OSX/Windows)
```bash
    ./2smart.sh write --device <DEVICE>
```

3. When process completed turn off and on device again.

4. If everything is okay it should appear in web-interface and mobile app.

#### With docker (Linux)

1. Open folder after unzipping downloaded archive in terminal (there should be config file .yml and folder with build):
```bash
    $ cd <unzipped_archive>
    $ ls -la .
    total 2136
    drwx------@ 12 user  group     384 Mar 15 12:52 .
    drwx------@ 34 user  group    1088 Mar 15 12:52 ..
    -rwxr-xr-x@  1 user  group    3684 Mar 15 10:51 2smart.sh
    -rwxr-xr-x@  1 user  group    4228 Mar 15 10:51 2smart_docker.sh
    -rw-r--r--@  1 user  group   12248 Mar 15 10:51 2smartota.py
    -rw-r--r--@  1 user  group    4145 Mar 15 10:51 README.md
    -rw-r--r--@  1 user  group    8192 Mar 15 10:51 boot_app0.bin
    -rw-r--r--@  1 user  group   15872 Mar 15 10:51 bootloader_dio_40m.bin
    -rw-r--r--@  1 user  group     704 Mar 15 10:51 device1702611907531972.yml
    -rw-r--r--@  1 user  group  143640 Mar 15 10:51 esptool.py
    -rw-r--r--@  1 user  group  876992 Mar 15 10:51 firmware.bin
    -rw-r--r--@  1 user  group    3072 Mar 15 10:51 partitions.bin
```

2. Use our custom ESPHome [docker image](https://hub.docker.com/r/2smartdev/esphome) to flash a device with compiled firmware
```bash
    ./2smart_docker.sh esphome_run --device <DEVICE> --id device1702611907531972
```

3. When process completed turn off and on device again.

4. If everything is okay it should appear in web-interface and mobile app.

## Useful links

1. [2Smart Cloud ESPHome documentation](https://github.com/2SmartCloud/2smart-cloud-esphome)
2. [Official ESPHome documentation](https://esphome.io/)
3. [How to create a Wi-Fi switch to control via a mobile app and Telegram bot](https://2smart.com/blog/tpost/2n6ankych1-how-to-create-a-wi-fi-switch-to-control)
