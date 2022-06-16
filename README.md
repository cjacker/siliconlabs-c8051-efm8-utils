# Standalone C8051/EFM8 flash tool for x86-64 linux from Silicon Labs

Standalone C8051/EFM8 flash tool (device8051, flash8051 and flashefm8) support jtag/c2 with Silicon labs' usb debug adapter and EFM8 Starter Kit with Toolstick or Jlink debugger on board.

These utilities located at `SimplicityStudio_v5/developer/adapter_packs`, and part of them is opensource, you can find the source code of `libslabhiddevice.so` in https://www.silabs.com/documents/public/software/USBXpressHostSDK-Linux.tar and the headers for `libslab8051.so` at https://community.silabs.com/s/article/linux-flash-programming-utilities-for-efm8-c8051fxxx?language=en_US

Thanks Silicon Labs for native Linux support.

# device8051 usage

device8051 detect and display C8051/EFM8 device informations.

```
Utility for detecting Silabs 8051 devices.

Usage: device8051 -?|-slist
  -?           show this help message.
  -slist       list all detected 8051 devices.
```

For example:

```
sudo device8051 -slist
```

For U-EC3 usb debug adapter connected with C8051F320, the output looks like:

```
deviceCount = 1
device (EC3T0120100) {
  adapterLabel = USB Debug Adapter
  SerialNo = EC3T0120100
  targetInterface = c2
  Name = C8051F320
  Type = MCU
  Family = 8051
  BoardID =
  BoardCount = 0
  HardwareID = 0x9
  DerivativeID = 0x58
  HardwareRev = 0x3
  DerivativeRev = 0x6
  Unsupported = 0
  Indeterminate = 0
  Connected = 0
  Locked = 0
}
```

For EFM8BB1LCK starter kit, the output looks like:

```
deviceCount = 1
device (LCK0081654) {
  adapterLabel = EFM8LCK
  SerialNo = LCK0081654
  targetInterface = c2
  Name = EFM8BB10F8G-QSOP24
  Type = MCU
  Family = 8051
  BoardID = efm8bb1lcba
  BoardCount = 1
  HardwareID = 0x30
  DerivativeID = 0x1
  HardwareRev = 0x2
  DerivativeRev = 0xb
  Unsupported = 0
  Indeterminate = 0
  Connected = 0
  Locked = 0
}
```

# flash8051 usage

To program the C8051Fxxx device or EFM8 with usb debug adapter such toolstick and U-ECx, you should use `flash8051`.

```
Utility for programming flash of 8051 devices.
Copyright (c) Silicon Labs 2015.

Usage: flash8051 [options]
  -?                show this help message.
  -sn               serial number of the device (decimal number) to flash.
  -tif              target interface, 'c2' or 'jtag'.
  -upload file      upload a file to device flash, an OMF or Hex file.
  -erase            erase flash.
  -lock             lock device flash.
  -unlock           unlock device flash.
  -checklocked      check if device flash is locked. Output true or false.
  -erasemode <mode> how to erase memory before flashing ('full'*, 'page', or 'merge')
  -clkstrobe <speed>C2 Clock strobe speed
  -keeppower <t|f>   boolean indicating whether to power after disconnect
```

For example, to program the EFM8BB10F8G_QSOP24 UART bootloader to EFM8BB1LCK starter kit  (connect it with a Micro USB cable directly to PC)

```
sudo flash8051 -sn LCK0081654 -tif c2 -erasemode full -upload EFM8BB10F8G_QSOP24.hex
```

The `EFM8BB10F8G_QSOP24.hex` is UART bootloader from [AN945SW](https://www.silabs.com/documents/public/example-code/AN945SW.zip).

You can use `device8051` to detect the 'serial number' and 'target interface', or use `dmesg` after device plugged in, it looks like:

```
[ 1456.424413] usb 1-3: Product: EFM8LCK
[ 1456.424417] usb 1-3: Manufacturer: Silicon Laboratories
[ 1456.424420] usb 1-3: SerialNumber: LCK0081654
```

# flashefm8 usage
To program the EFM8 device with J-Link, you should use `flashefm8`.

```
Utility for programming flash of EFM8 devices.
Copyright (c) Silicon Labs 2015.

Usage: flashefm8 [options]
  -?                show this help message.
  -sn               serial number of the device (decimal number) to flash.
  -ip <host|ip>     work with device over TCP/IP.
  -tif              target interface, 'c2' or 'jtag'.
  -part             part name
  -upload file      upload a file to device flash, an OMF or Hex file.
  -erase            erase flash.
  -lock             lock device flash.
  -unlock           unlock device flash.
  -checklocked      check if device flash is locked. Output true or false.
  -erasemode <mode> how to erase memory before flashing ('full'*, 'page', or 'merge')
  -jlinkspeed <spd> jlink speed in hz
```

The usage of `flashefm8` is as same as `flash8051`.

Take the EFM8SB1 STK as example to program the on-board part you could use command:

```
sudo flashefm8 -sn 000440033272 -tif c2 -part efm8sb10f8g -upload EFM8SB1_Oscillator_CMOS.hex -erasemode page
```

# udev rules
All above commands run with `sudo`. to avoid using `sudo`, please copy '98-silabs.rules' and '99-silabs-jlink.rules' to '/etc/udev/rules.d' and run:

```
sudo udevadm control --reload-rules
sudo udevadm trigger
```
