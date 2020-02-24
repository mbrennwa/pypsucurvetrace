# curvetracePPSPy
Python code to use Voltcraft PPS power supplies as curve tracers

## Prerequisites
* curvetracePPSPy was (and is) developed using Python 3 on Linux. Other software environments may (should) work, too, but have not been tested so far.
* For DUTs with two terminals (resistors, diodes, etc.), your need only one PPS.
* For DUTs with three terminals (transistors and similar parts) you need two PPS.

## Installation and configuration
* Download the code from the GitHub repository, either using GIT, SVN or as a ZIP archive.
I like SVN (subversion): svn co https://github.com/mbrennwa/curvetracePPSPy.git/trunk path/on/your/computer/to/curvetracePPSPy
* Connect your Voltcraft PPS power supplies to your computers USB.
* Copy the config_PPS_TEMPLATE.txt file to config_PPS.txt, and modify the file to reflect the details of your USB/Serial PPS interfaces. NOTE: Most Voltcraft PPS power supplies use the same Serial device ID. If you want to use more than one PPS unit, you will need to modify the device IDs so they are not identical. See "Notes" section below for details.
* Make sure your user account has permissions to access the serial ports of the PPS units. See "Notes" section below.

## Usage
* Connect the DUT to the output terminals of the PPS power supplies.
* Open a terminal window and execute the curvetrace program. Follow the on-screen instructions.

## Notes

### Modify serial device IDs of the Voltcraft PPS power supplies
In their stock condition, the Silabs CP2102 USB/serial interfaces of the Voltcraft PPF power supplies all use the same ID. The serial interfaces of multiple PPS units connected to the same computer therefore show up at the same file node under /dev/serial/by-id/ (usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0 or similar). In order to simultaneously use more than one PPS unit, the serial interface IDs therefore need to be reconfigured to use unique IDs. This is achieved using the cp210x-cfg program:

* Download cp210x-cfg code:
svn co https://github.com/DiUS/cp210x-cfg.git

* Install USB library stuff needed to compile the cp210x-cfg program:
sudo apt install libusb-1.0-0-dev 

* Compile the cp210x-cfg program:
cd path/to/cp210x-cfg/
make

* Display HELP information for cp210x-cfg, and make *sure* you understand how the program works:
./cp210x-cfg -h

* List all Silabs CP210x devices connected to the computer:
./cp210x-cfg -l
ID 10c4:ea60 @ bus 002, dev 031: CP2102 USB to UART Bridge Controller

* Make sure only one Silabs CP210x interface is connected (the PPS unit one you want to reconfigure), then show its information:
./cp210x-cfg

* Change the Serial ID of the device:
./cp210x-cfg -S 0002

* Plug in the other PPS device and make sure that both serial interfaces now show up separately at /dev/serial/by_id:
ls /dev/serial/by-id

PSU1: /dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0
PSU2: /dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0002-if00-port0

### Set user permissions to access serial ports
...
