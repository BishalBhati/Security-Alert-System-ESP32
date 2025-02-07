#!/usr/bin/env bash

help() {
    cat <<HELP

    Simplify esptool commands

    Usage: ./2smart.sh COMMAND [FLAGS]

    Commands:
        write [-d|--device DEVICE]                                      write build to device
        write_ota [-p|--PORT PORT] [-h|--host HOST] [-s|--pass PASS]    write build to device over the air (OTA)
        logs [-d|--device=DEVICE]                                       view device logs
        erase_flash                                                     erase flash from device
    Flags:
        -d|--device DEVICE         device which appear after connectig microcontroller to your PC
        -h|--host HOST             host of device where firmware is running
        -p|--port PORT             port on device where firmware is running (optional, 3232 by default)
        -s|--pass PASS             password to connect over the air (OTA)

HELP
}

erase_flash() {
    check_is_missing_args

    esptool_command="python3 esptool.py erase_flash"

    printf "running esptool command:\n$esptool_command\n"
    eval $esptool_command
}


write() {
    if [ -z $DEVICE ] 
        then
        echo "MISSNG ARGUMENT: -d|--device DEVICE is required"
        IS_ARGS_MISSING=1
    fi
    if [ ! -z $IS_ARGS_MISSING ] 
        then
        help
        exit 1
    fi

    esptool_command="python3 esptool.py \
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
        0x1000 bootloader_dio_40m.bin \
        0x8000 partitions.bin \
        0xe000 boot_app0.bin \
        0x10000 firmware.bin"
    printf "running esptool command:\n$esptool_command\n"
    $esptool_command
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
    if [ ! -z $IS_ARGS_MISSING ] 
        then
        help
        exit 1
    fi

    smartota_command="python3 2smartota.py \
        --host $HOST \
        --port $PORT \
        --password $PASS \
        --filename firmware.bin"
    printf "running 2smartota command:\n$smartota_command\n"

    $smartota_command
}

logs() {
    if [ -z $DEVICE ]
        then
        echo "MISSNG ARGUMENT: -d|--device DEVICE is required"
        IS_ARGS_MISSING=1
    fi
    if [ ! -z $IS_ARGS_MISSING ]
        then
        help
        exit 1
    fi
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
        write|write_ota|logs|erase_flash)
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
