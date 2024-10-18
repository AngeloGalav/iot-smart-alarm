@REM Program to reflash esp32 micropython

@echo off
set port=%1
IF %1.==. GOTO No1

echo erasing esp32 memory...
esptool.exe --chip esp32 --port %port% erase_flash
echo reflashing esp32 with micropython...
esptool.exe --chip esp32 --port %port% --baud 460800 write_flash -z 0x1000 ESP32_firmware.bin
GOTO End1

:No1
  echo No port issued!
:End1
