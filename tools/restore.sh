#!/bin/bash
# Program to reflash esp32 with micropython, linux version

port=$1

if [ -z "$port" ]; then
  echo "No port issued!"
  exit 1
fi

echo "Erasing esp32 memory..."
esptool.py --chip esp32 --port /dev/"$port" erase_flash

echo "Reflashing esp32 with micropython..."
esptool.py --chip esp32 --port /dev/"$port" --baud 460800 write_flash -z 0x1000 ESP32_firmware.bin
