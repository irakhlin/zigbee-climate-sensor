- [ClimateSense](#climatesense)
  * [Description](#description)
  * [Features](#features)
  * [Device Basics](#device-basics)
    + [Factory Reset](#factory-reset)
  * [Flashing Instructions](#flashing-instructions)
    + [Method 1: Preferred](#method-1--preferred)
    + [Method 2: If auto BSL is not working](#method-2--if-auto-bsl-is-not-working)
    + [Method 2b: GUI version but Windows only](#method-2b--gui-version-but-windows-only)
    + [Method 3: Worst case scenario](#method-3--worst-case-scenario)
  * [Setup](#setup)
    + [ZHA setup](#zha-setup)
        * [Additional ZHA docs:](#additional-zha-docs-)
  * [Zigbee2mqtt setup](#zigbee2mqtt-setup)

# ClimateSense

## Description

## Features

## Device Basics

 - Green LED:
	 - Blinks when device is either attempting to join a zigbee network or has not yet joined a zigbee network. 
	 - Blinking will stop when the device joins a network, will restart blinking if removed from the network.
- Red LED:
	 - This LED is meant as a locator LED, in case there are multiple devices in a location and there is a need to locate a specific one. It will be on during the initial configuration of the device.
	 -  After the device has joined a Zigbee network and been successfully interviewed home assistant will create an "on/off" switch entity for the device, this will allow to turn the LED on or off as desired.
- RST Button: (On left with USB pointing down)
	- Simple tap restarts the device, equivalent of unplugging and plugging back into power
- BSL Button: (On right with USB pointing down)
	- Can be used to boot device into boot loader mode
	- If device is joined to a network, holding down the BSL button for 10 seconds will factory reset the device. It is best to first remove the device from the coordinator in software as then the coordinator will send the proper reset command automatically and prevent the possibility of on the coordinator side. 

### Factory Reset
Method 1: 


## Flashing Instructions

### Method 1: Preferred
This board contains a small auto BSL circuit that allows the device to be put into bootloader mode automatically via toggling of the DTS and RTS pins on the UART chip. This option is already built into cc2538-bsl, the recommended utility for doing (windows and Linux compatible). [Link](https://github.com/JelmerT/cc2538-bsl)

The specific command line flag needed is "--bootloader-sonoff-usb". 

The following example will boot the device into boot loader mode, erase, write and verify the firmware for the device connected on COM6 (check control panel for the COM port number) using the firmware file 'climatesense1.0.hex'
``` 
python cc2538-bsl.py -ewv --bootloader-sonoff-usb -p COM6 climatesense1.0.hex
```
or on Linux..
```
python cc2538-bsl.py -ewv --bootloader-sonoff-usb -p /dev/ttyUSB0 climatesense1.0.hex
```
### Method 2: If auto BSL is not working
If the device is failing to enter boot loader mode automatically it can be done manually. 1. Before plugging in the device locate the button labeled "BSL" (bottom right if the USB port is pointing down).
2. Before plugging in the device hold down the BSL button, it must be held down as the device is plugged into the USB port.
3. Continue to hold the BSL button for 5-7 seconds after it has been inserted into USB.
4.  Proceed to flashing without the boot loader flag.
```
python cc2538-bsl.py -ewv -p /dev/ttyUSB0 imanz.climatesense1.0.hex
```

### Method 2b: GUI version but Windows only
Texas Instruments provide a windows GUI utility for performing the same process as in method 2, auto BSL however will not work like in method 1 so boot loader mode will need to be entered manually. Only really recommended if you are having some specific issue with cc2538-bsl.py. More information can be found [here](https://electrolama.com/radio-docs/flash-ti-flash-prog/)

### Method 3: Worst case scenario
The small black 8 pin connector allows access to the DEBUG pins on the CC2652p but the arrangement has been slightly modified for space. This method also requires a JTAG compatible device.
**TODO: add custom debugger board pin layout**
Links:
[JTag Flashing](https://electrolama.com/radio-docs/advanced/flash-jtag/)

## Setup
Depending on the home assistant installation type (docker, python native, supervised) the instructions to setup a basic Zigbee coordinator may be slightly different. There are two Zigbee integrations, zigbee2mqtt or ZHA ( built into HA), I personally use zigbee2mqtt installed from the "addon store" in a "fully suprvised hassio OS install", but have also tested in ZHA.

### ZHA setup
ZHA uses the concepts of "quirk" files which are used to help ZHA translate the devices specific "configurations" to proper properties. Before adding the device you must add a quirk directory, add the provided quirk and restart home assistant.

 1. Inside the Home Assistant configuration directory create a directory called custom_zha_quirks
```
cd /home/homeassistant/.homeassistant && mkdir custom_zha_quirks
```
2. Copy the provided quirk from converters/climatesense1.0.py to the directory and set correct permission
```
cd /home/homeassistant/.homeassistant/custom_zha_quirks
wget https://raw.githubusercontent.com/irakhlin/zigbee_climate_sensor/main/converters/climatesense1.0.py 
chown -R homeasistant:homeassistant /home/homeassistant/.homeassistant/custom_zha_quirks
chmod 644 /home/homeassistant/.homeassistant/custom_zha_quirks/climatesense1.0.py
```

3. Add the custom quirk directory path to your home assistant configuration file.
```
zha:
  enable_quirks: true
  custom_quirks_path: /home/homeassistant/.homeassistant/custom_zha_quirks
```
4. Restart home assistant
5. Proceed to add the device as normal in ZHA
6. After the device has finished the interview process all property entities may not be created because of the way ZHA handles the custom quirk. If you do not see temperature/humidity entities for the newly added device simply restart home assistant and they will be generated.

##### Additional ZHA docs:
[Home Assistant ZHA Documentation](https://www.home-assistant.io/integrations/zha/)
[ZHA Quirks](https://github.com/zigpy/zha-device-handlers#testing-quirks-in-development-in-docker-based-install)

## Zigbee2mqtt setup

Zigbee2mqtt uses a concept called herdsman converters, which are essentially the same idea as a ZHA quirk but written in javascript using their own zigbee library. A custom herdsman converter is provided in converters/climatesense1.0.js
1. Navigate to the zigbee2mqtt install directory and download the converter file
```
cd /opt/zigbee2mqtt
wget https://raw.githubusercontent.com/irakhlin/zigbee_climate_sensor/main/converters/climatesense1.0.js
chmod 755 /opt/zigbee2mqtt/climatesense1.0.js
```
2. Add the following to the configuration file for zigbee2mqtt
```
external_converters:
  - climatesense1.0.js
```
3. Restart and proceed to add device as normal


This may also be possible though the zigbee2mqtt GUI, see links below for more information.

[Zigbee2MQTT converter configuration](https://www.zigbee2mqtt.io/guide/configuration/more-config-options.html#external-converters)
[Herdsman converter](https://github.com/Koenkk/zigbee-herdsman-converters)