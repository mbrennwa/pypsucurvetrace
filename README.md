# PyPSUcurvetrace
*PyPSUcurvetrace* is a software toolbox for I/V curve tracing of electronic parts using programmable power supplies. In short, *PyPSUcurvetrace* is a *curve tracer*.

For two-terminal devices under test (DUTs) like resistors or diodes you need only one power supply unit (PSU). For three-terminal DUTs like transistors you need two PSUs.

*PyPSUcurvetrace* also allows using a heater block to control the temperature of the DUT.

*PyPSUcurvetrace* is developed using Python 3 on Linux. Other software environments may (should) work, too, but have not been tested so far.

Currently supported power supply types:
* Voltcraft PPS
* Korad / RND (confirmed: models KA3005P and KWR103, other models not tested)
* BK Precision (confirmed: model BK9185B, 9120A, other models not tested)

Power supply types on the radar for future support:
* Units with a SCPI interface

*PyPSUcurvetrace* is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. *PyPSUcurvetrace* is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with *PyPSUcurvetrace*. If not, see [http://www.gnu.org/licenses/](http://www.gnu.org/licenses/).

## How does it work?


### Overview
The following figure shows the basic test circuit for a three-terminal DUT with two PSUs:
![alt text](https://github.com/mbrennwa/PyPSUcurvetrace/blob/master/figures/test_setup.png "Basic test circuit")

For two-terminal DUTs, only PSU1 is needed and PSU2 can be ignored. If negative voltages are required at the DUT terminals, the respective PSU terminals are connected with inverted polarity.

Tests are run using the `curvetrace` program. `curvetrace` tests the DUT by varying the voltages V1 and V2 at the PSU terminals, and by reading the corresponding currents I1 and I2. The results are shown on the screen and saved in an ASCII data file for further processing.

Here's a photo showing the test setup for a power MosFET using two RND/Korad PSUs:
![alt text](https://github.com/mbrennwa/PyPSUcurvetrace/blob/master/figures/test_power_MosFET_photo.jpg "Power MosFET test setup")

`curvetrace` provides different methods to control the DUT temperature during the test. Firstly, `curvetrace` may insert idle periods in between the individual readings, or a "pre-heat" period before starting the test, where the voltages (V1, V2) and currents (I1, I2) applied to the DUT are set to predefined ``idle'' values. Secondly, `curvetrace` can use a heater block equipped with a heater element and temperature sensor for active control of the DUT temperature (full heaterblock documentation is pending). Here's a photo of a temperature controlled heaterblock using power resistors as heaters and a Maxim DS18B20 temperature sensor:
![alt text](https://github.com/mbrennwa/PyPSUcurvetrace/blob/master/figures/heaterblock_photo.jpg "Heaterblock for temperature controlled DUT testing")

`curvetrace` also offers some special operation modes:
* "batch": sequential measurement of parts using the same DUT configuration
* "quick": run "pre-heat" only, skip the curve tracing (can be useful for matching parts based on the idle operating point)

The procedure implemented in the `curvetrace` program is as follows:
1. Read a configuration file with the types and serial ports of the programmable PSUs, and then establish the serial connection to the PSUs.
2. Interactively ask the user for a name or label of the test data, and then open an ASCII data file with that name (an existing file with the same name gets overwritten!).
3. Determine the test conditions, either by interactively asking for user input, or by reading a configuration file with the test parameters:
* Start voltages, end voltages, and number of steps for each PSU
* Max. allowed current and power applied from each PSU to the DUT
* Polarity of how the PSU terminals are connected to the DUT terminals
* Optional: number of readings at each voltage step (results will be averaged)
* Optional: idle time and pre-heat time
* If idle or pre-heat times are not zero: idle voltage and current conditions for the PSUs
* Optional: DUT temperature
4. Check the test configuration versus the limits of the PSUs, and adjust the configuration where needed.
5. Show a summary of the test configuration and ask the user if it's okay to start the test.
6. Run the test:
* If a heaterblock is used: wait until the DUT has attained the specified temperature.
* The voltages are stepped in two nested loops. Voltage V1 is varied in the inner loop, V2 is varied in the outer loop.
* The measured data are shown on the screen and saved to the data file.
7. Once the test is completed, turn off the PSUs.

### Details
* For each step of the test procedure (measurement, idle, or pre-heat), `curvetrace` sets the voltages at the PSUs according to voltage values requested for this step. The current values of the PSUs are set to the minima of the current and power limits of the DUT and the PSUs at the given test voltages. If the currents established by the DUT are less than the current limits set at the PSUs, the PSUs will operate in "voltage limiting" mode, so that the voltage values required for this test step will be present at the DUT terminals. If the currents established by the DUT reach the current limits set at the PSUs, it is the task of the PSUs to avoid the currents from exceeding the limits by switching to "current limiting" mode, lowering the voltage values applied to the DUT. `curvetrace` reports the occurrence of "current limiting" mode in the data output using "Current Limit" flags.
* Once the inner loop (iteration of V1 steps) reaches a point where either I1 or I2 run into the current or power limits of the DUT or the PSUs, `curvetrace` stops the V1 iterations of the inner loop and returns to the next V2 iteration of the outer loop.
* Once a test voltage has been programmed at a PSU for a DUT measurement, `curvetrace` reads the voltage at the PSU terminals and waits for stabilisation of the read-back output voltage at the set point before continuing. This ensures that measurements are taken only after the voltages applied to the DUT have stabilised at the requested values.
* Some PSU types provide unreliable readings of the voltage or current values if the readings are taken too early after programming a new set point. To improve the reliability of the data obtains from such PSUs, `curvetrace` can be configured to take repeated readings with short idle periods in between. Readings are taken continuously until a specified number of consecutive readings are consistent within the readback resolution of the PSU, and the mean of those readings is returned as the measurement result. This method helps achieving stable, low-noise readings. For configuration of this feature, see the "PSU configuration file" section below.

## Software installation and configuration
* Download the code from the GitHub repository, either using GIT, SVN or as a ZIP archive.
I like SVN (subversion):
```
svn co https://github.com/mbrennwa/PyPSUcurvetrace.git/trunk path/on/your/computer/to/PyPSUcurvetrace
```
* Install the Python-3 Serial package. On Debian, Ubuntu or similar APT-based Linux systems:
```
sudo apt install python3-serial
```
* Connect your PSUs to the USB or serial ports of your computer and determine their serial port interfaces on your system.
On Linux:
```
ls /dev/serial/by-id
```
* Copy the `config_PSU_TEMPLATE.txt` file to `config_PSU.txt`. Modify the file to reflect the details of the USB/serial interfaces of your your PSUs. See "Notes" section for further information on the PSU configuration file.
* *NOTE:* By default, most Voltcraft units use the same serial device ID. Therefore, it is not possible to access more than one PSU unit via `/dev/serial/by-id/`. If you want to use more than one PSU unit, you will need to modify the device IDs of the serial interfaces so that they are different from each other. See "Notes" section below for details.
* Make sure your user account has permissions to access the serial ports of the PSU units. See "Notes" section below.

## Usage
To run the software, execute the `curvetrace` program from a console terminal.
  * The easiest method is to run the program without any arguments and just follow thew the on-screen instructions for fully interactive user input:
  ```
  curvetrace
  ```
  * You can also use provide a configuration file containing the test parameters (see example files provided). For example:
  ```
  curvetrace -c examples/test_config/2SK216_config.txt
  ```
  See "Notes" section for further information on test configuration files.

## Examples

### IRFP150 N-channel power mosfet
This example shows curve traces obtained from an IRFP150 N-channel power mosfet (drain current I<sub>D</sub> vs. drain-source voltage V<sub>DS</sub>, measured at different gate-source voltages V<sub>GS</sub>). The IRFP150 pins and PSU outputs were connected according to above diagram.
* DUT source pin to the negative terminals of PSU1 and PSU2 (joined together)
* DUT drain pin to the positive terminal of PSU1
* DUT gate pin to the positive terminal of PSU2. A gate stopper resistor was used to avoid oscillation.
The power limit for the test was set to 100 W. The curves were recorded at fixed temperatures of 30°C, 50°C and 70°C using a heaterblock for temperature control (see photo above).
![alt text](https://github.com/mbrennwa/PyPSUcurvetrace/blob/master/figures/IRFP150_curves_heaterblock.png "IRFP150 curves at 30°C, 50°C and 70°C")


### 2SJ79 P-channel mosfet
This example shows curve traces obtained from an 2SJ79 P-channel mosfet (drain current I<sub>D</sub> vs. drain-source voltage V<sub>DS</sub>, measured at different gate-source voltages V<sub>GS</sub>). The 2SJ79 was connected in the same way as the IRFP150 in the previous example, but with the polarity of the PSU terminals inverted to obtain negative test voltages:
* DUT source pin to the positive terminals of PSU1 and PSU2 (joined together)
* DUT drain pin to the negative terminal of PSU1
* DUT gate pin to the negative terminal of PSU2. A gate stopper resistor was used to avoid oscillation.
![alt text](https://github.com/mbrennwa/PyPSUcurvetrace/blob/master/figures/2SJ79_curves.png "2SJ79 curves")


### 6C33C power triode
This example shows curve traces obtained from an 6C33C power triode (anode current vs. anode-cathode voltage, measured at different negative grid-cathode voltages V<sub>GS</sub>). The 6C33C was connected as follows
* DUT anode pin to the positive terminals of PSU1
* DUT cathode pin to the negative terminal of PSU1 and positive terminal of PSU2 (joined together)
* DUT gate pin to the negative terminal of PSU2.
For this test, only one high-voltage power supply (PSU1) was available. The second power supply (PSU2) was therefore configured as a 90 V PSU made up by a series connection of a 30 V PSU and a 60 V PSU (see below for configuration of such a series combination).

![alt text](https://github.com/mbrennwa/PyPSUcurvetrace/blob/master/figures/6C33C_curves.png "6C33C curves")


## Notes

### PSU configuration file
The configuration file `config_PSU.txt` contains the configuration details of your power supplies (PSUs). Take a look at the `config_PSU.txt` for details of the file format. There are separate sections for PSU1 and PSU2. Each section contains the following fields:
* `COMPORT`: virtual file corresponding to the serial port of the PSU
* `COMMANDSET`: the "language" for communication with the PSU. Currently supported `COMMANDSET`s are
	* `VOLTCRAFT` for Voltcraft, Manson, etc.
	* `KORAD` for Korad, RND, etc.
	* `BK`, `BK9184B_LOW`, `BK9184B_HIGH`, `BK9185B_LOW`, and `BK9185B_HIGH` for BK Precision.
* `NUMSTABLEREAD` (optional): number of consecutive readings that must agree to within the measurement resolution in order to achieve stable and low-noise readings

If only one PSU is used (PSU1), the PSU2 section can be deleted.

Note that it is possible to connect multiple PSU units in series to each other to accomplish a higher voltage range. Such a series combination of multiple PSU units can be configured as a single PSU object by specifying their `COMPORT` and `COMMANDSET` fields as follows:
* `COMPORT = ( "/dev/serial/by-id/<xxx_psu1>" , "/dev/serial/by-id/<xxx_psu2>" )`
* `TYPE = ( "<commandset_psu1>" , "<commandset_psu2>" )`

### Test configuration file
...(under constrution -- take a look at the example files in the `examples` directory.)...

### Set user permissions to access serial ports (Linux)
To allow accessing the serial ports, add your username to the `dialout` group. For example, if your user account is `johndoe`, execute the following command:
```
sudo adduser johndoe dialout
```
Then log out and log in again to the user account `johndoe` for this to take effect.

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
