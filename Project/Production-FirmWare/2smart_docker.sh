#!/usr/bin/env bash

help() {
    cat <<HELP

    Simplify docker esptool/esphome commands

    Usage: ./2smart_docker.sh COMMAND [FLAGS]

    Commands:
        write [-d|--device DEVICE]                                      write build to device
        write_ota [-p|--PORT PORT] [-h|--host HOST] [-s|--pass PASS]    write build to device over the air (OTA)
        esphome_run [-d|--device DEVICE] [-i|--id DEVICE_ID]            run recompile and rewrite using device yml config (linux only)
        esphome_compile [-i|--id DEVICE_ID]                             compile using device yml config
        copy [-p|--product PRODUCT_ID]                                  copy and replace binaries from new compilation
        logs [-d|--device DEVICE]                                       view device logs
        erase_flash                                                     erase flash from device
    Flags:
        -d|--device DEVICE         device which appear after connectig microcontroller to your PC
        -i|--id DEVICE_ID          device identifier in 2Smart Cloud platform
        -p|--product PRODUCT_ID    product identifier in 2Smart Cloud platform
        -h|--host HOST             host of device where firmware is running
        -p|--port PORT             port on device where firmware is running (optional, 3232 by default)
        -s|--pass PASS             password to connect over the air (OTA)

HELP
}

PWD_OUTPUT="$(pwd)"
PWD_ESCAPED=$(printf %q "$PWD_OUTPUT")

erase_flash() {
    check_is_missing_args

    esptool_command="docker run --rm \
        --device=$DEVICE \
        -it 2smartdev/esptool esptool.py erase_flash"

    printf "running esptool command:\n$esptool_command\n"
    eval $esptool_command
}

write() {
    if [ -z $DEVICE ] 
        then
        echo "MISSNG ARGUMENT: -d|--device DEVICE is required"
        IS_ARGS_MISSING=1
    fi

    check_is_missing_args

    esptool_command="docker run --rm \
        -v "${PWD_ESCAPED}":/firmware_build \
        --device=$DEVICE \
        -it 2smartdev/esptool esptool.py \
            --chip esp32 \
            --port $DEVICE \
            --baud 115200 \
            --before default_reset \
            --after hard_reset \
            write_flash \
            -z \
            --flash_mode dio \
            --flash_freq 40m \
            --flash_size detect \
            0x1000 /firmware_build/bootloader_dio_40m.bin \
            0x8000 /firmware_build/partitions.bin \
            0xe000 /firmware_build/boot_app0.bin \
            0x10000 /firmware_build/firmware.bin"
    printf "running esptool command:\n$esptool_command\n"
    eval $esptool_command
}

write_ota() {
    if [ -z $HOST ] 
        then
        echo "MISSNG ARGUMENT: -h|--host HOST is required"
        IS_ARGS_MISSING=1
    fi
    if [ -z $PASS ] 
        then
        echo "MISSNG ARGUMENT: -s|--pass PASS is required"
        IS_ARGS_MISSING=1
    fi
    if [ -z $PORT ]
        then
        PORT=3232
    fi

    check_is_missing_args

    smartota_command="docker run --rm \
        -v "${PWD_ESCAPED}":/firmware_build \
        --net=host \
        -it 2smartdev/esptool 2smartota.py \
            --host $HOST \
            --port $PORT \
            --password <PASSWORD> \
            --filename /firmware_build/firmware.bin"
    printf "running 2smartota command:\n$smartota_command\n"

    eval $smartota_command
}

esphome_run() {
    if [ -z $DEVICE_ID ] 
        then
        echo "MISSNG ARGUMENT: -i|--id DEVICE_ID is required"
        IS_ARGS_MISSING=1
    fi

    check_is_missing_args

    run_command="docker run --rm -v "${PWD_ESCAPED}":/config --device=/dev/ttyUSB0 -it 2smartdev/esphome /config/${DEVICE_ID}.yml run"

    printf "running 2smart compile command:\n$run_command\n"

    eval $run_command
}

esphome_compile() {
    if [ -z $DEVICE_ID ] 
        then
        echo "MISSNG ARGUMENT: -i|--id DEVICE_ID is required"
        IS_ARGS_MISSING=1
    fi

    check_is_missing_args

    compile_command="docker run --rm -v "${PWD_ESCAPED}":/config -it 2smartdev/esphome /config/${DEVICE_ID}.yml compile"

    printf "running 2smart compile command:\n$compile_command\n"

    eval $compile_command
}

copy() {
    if [ -z $PRODUCT_ID ] 
        then
        echo "MISSNG ARGUMENT: -p|--product PRODUCT_ID is required"
        IS_ARGS_MISSING=1
    fi
     
    check_is_missing_args

    eval "cp $PWD_ESCAPED/$PRODUCT_ID/.pioenvs/$PRODUCT_ID/firmware.bin ."
    eval "cp $PWD_ESCAPED/$PRODUCT_ID/.pioenvs/$PRODUCT_ID/partitions.bin ."
}

logs() {
    if [ -z $DEVICE ]
        then
        echo "MISSNG ARGUMENT: -d|--device DEVICE is required"
        IS_ARGS_MISSING=1
    fi

    check_is_missing_args

    serial_tools_command="python3 -m serial.tools.miniterm $DEVICE 115200"
    printf "running serial.tools.miniterm command:\n$serial_tools_command\n"

    $serial_tools_command
}

check_is_missing_args() {
    if [ ! -z $IS_ARGS_MISSING ]
        then
        help
        exit 1
    fi
}

if [[ $# == 0 ]]; then
    help
    exit 1
fi

ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--device)
            read -ra val <<< "$2"
            if [ -z $2 ]; then help && exit 1; fi

            DEVICE=$2
            shift 2
            ;;
        -p|--port)
            read -ra val <<< "$2"
            if [ -z $val ]; then help && exit 1; fi

            PORT=$val
            shift 2
            ;;
        -h|--host)
            read -ra val <<< "$2"
            if [ -z $val ]; then help && exit 1; fi

            HOST=$val
            shift 2
            ;;
        -s|--pass)
            read -ra val <<< "$2"
            if [ -z $val ]; then help && exit 1; fi

            PASS=$val
            shift 2
            ;;
        -i|--id)
            read -ra val <<< "$2"
            if [ -z $val ]; then help && exit 1; fi

            DEVICE_ID=$val
            shift 2
            ;;
        -p|--product)
            read -ra val <<< "$2"
            if [ -z $val ]; then help && exit 1; fi

            PRODUCT_ID=$val
            shift 2
            ;;
        write|write_ota|logs|esphome_run|esphome_compile|copy|erase_flash)
            COMMAND=$1
            shift
            ;;
        -h|--help)
            help
            exit 0
            ;;
        *)
            printf "\e[31mcommand '%s' is not supported\e[0m\n" "$1"
            help
            exit 1
            ;;
    esac
done

printf -v args "%s" "${ARGS[@]}"

"$COMMAND" "$args"
