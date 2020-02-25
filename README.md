# curvetracePPSPy
*curvetracePy* is a Python 3 program that makes use of programmable power supplies to determine I/V curve traces of electronic parts. In short, *curvetracePy* is a *curve tracer*.

For two-terminal devices under test (DUTs) like resistors or diodes you need only one power supply unit (PSU). For three-terminal DUTs like transistors you need two PSUs.

*curvetracePy* is developed using Python 3 on Linux. Other software environments may (should) work, too, but have not been tested so far.

Supported power supply types:
* Voltcraft PPS

## Software installation and configuration
* Download the code from the GitHub repository, either using GIT, SVN or as a ZIP archive.
I like SVN (subversion):
```
svn co https://github.com/mbrennwa/curvetracePy.git/trunk path/on/your/computer/to/curvetracePy
```
* Connect your PSUs to the USB pots of your computer.
* Copy the `config_PSU_TEMPLATE.txt` file to `config_PSU.txt`, and modify the file to reflect the details of the USB/serial interfaces of your your PSUs. See "Notes" section for further information on the PSU configuration file.
* *NOTE:* By default, most Voltcraft units use the same serial device ID. Therefore, it is not possible to access more than one PSU unit via `/dev/serial/by-id/`. If you want to use more than one PSU unit, you will need to modify the device IDs of the serial interfaces so that they are different from each other. See "Notes" section below for details.
* Make sure your user account has permissions to access the serial ports of the PSU units. See "Notes" section below.

## Usage
The following figure shows the basic test setup for a three-terminal DUT with two PSUs:
![alt text](https://github.com/mbrennwa/curvetracePy/blob/master/figures/test_setup.png "Basic test setup")
For two-terminal DUTs, only PSU1 is needed and PSU2 can be ignored. If negative voltages are required to test the DUT terminals, the respective PSU terminals need to be connected with inverted polarity.

To run the software, execute the `curvetrace` program from a console terminal.
  * The easiest method is to run the program without any arguments and just follow thew the on-screen instructions for fully interactive user input:
  ```
  curvetrace
  ```
  * You can also use provide a configuration file containing the test parameters (see example files provided). For example:
  ```
  curvetrace -c test_config_examples/2SK214_config.txt
  ```
  See "Notes" section for further information on test configuration files.

## Examples

### IRFP150 power mosfet
This example shows curve traces obtained from an IRFP150 power mosfet (drain current I<sub>D</sub> vs. drain-source voltage V<sub>DS</sub>, measured at different gate-source voltages V<sub>GS</sub>). The IRFP150 pins and PSU outputs were connected according to above diagram.
* DUT source pin to GND
* DUT drain pin to the positive terminal of PSU1
* DUT gate pin to the positive termianl of PSU2. A 100 Ohm gate stopper resistor was used to avoid oscillation.
![alt text](https://github.com/mbrennwa/curvetracePy/blob/master/figures/IRFP150_curves.png "IRFP150 curves")

## Notes

### Modify serial device IDs of the Voltcraft PPS power supplies
In their stock condition, the Silabs CP2102 USB/serial interfaces of the Voltcraft PPF power supplies all use the same ID. The serial interfaces of multiple PPS units connected to the same computer therefore show up at the same file node under /dev/serial/by-id/ (usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0 or similar). In order to simultaneously use more than one PPS unit, the serial interface IDs therefore need to be reconfigured to use unique IDs. This is achieved using the `cp210x-cfg` program:

* Download the `cp210x-cfg` code:
```
svn co https://github.com/DiUS/cp210x-cfg.git
```

* Install USB library stuff needed to compile the `cp210x-cfg` program:
```
sudo apt install libusb-1.0-0-dev 
```

* Compile the `cp210x-cfg` program:
```
cd path/to/cp210x-cfg/
make
```

* Display HELP information for `cp210x-cfg`, and make *sure* you understand how the program works:
```
./cp210x-cfg -h
```

* Make sure only one Silabs CP210x interface is connected (the PPS unit one you want to reconfigure), then show its information:
```
./cp210x-cfg
```

* Change the serial ID of the device (don't mess this up!):
```
./cp210x-cfg -S 0002
```

* Plug in the other PPS device and make sure that both serial interfaces now show up separately at `/dev/serial/by_id`:
```
ls /dev/serial/by-id/
usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0
usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0002-if00-port0
```

### Set user permissions to access serial ports
To allow accessing the serial ports, add your username to the `dialout` group. For example, if your user account is `johndoe`, execute the following command:
```
sudo adduser johndoe dialout
```
Then log out and log in again to the user account `johndoe` for this to take effect.

### PSU configuration file
The configuration file `config_PSU.txt` contains the configuration details of your power supplies (PSUs). There are separate sections for PSU1 and PSU2. Each section contains the following fields
* `COMPORT`: virtual file corresponding to the serial port of the PSU
* `SETTLE_SECONDS`: time required to attain stable output after setting a new voltage or current value at the PSU (seconds)
* `VOLTAGE_MIN`: minium voltage value supported by the PSU (most Voltcraft PPS units have trouble to reliably set voltages lower than 0.85 V)

### Test configuration files
...(under constrution)...
