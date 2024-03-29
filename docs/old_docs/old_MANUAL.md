# PyPSUcurvetrace
*PyPSUcurvetrace* is a software toolbox for I/V curve tracing of electronic devices using programmable power supplies (PSUs). In short, *PyPSUcurvetrace* is a *curve tracer*.

For two-terminal devices under test (DUTs) like resistors or diodes, a single PSU is sufficient. For three-terminal DUTs like transistors (BJTs, FETs) or vacuum tubes, two PSUs are required (a single PSU box with two separate programmable outputs would also work).

*PyPSUcurvetrace* also allows using an optional heater block to control the temperature of the DUT during curve tracing. The heater block requires a dedicated PSU for temperature control.








## Data acquisition
The `curvetrace` program is used to acquire the test data. Basic documentation of the `curvetrace` program can be accessed by executing `curvetrace --help`.

The following figure shows the basic test circuit for for data acquisition using the `curvetrace` program with a three-terminal DUT with two PSUs:
![alt text](https://github.com/mbrennwa/PyPSUcurvetrace/blob/master/figures/test_setup.png "Basic test circuit")

For two-terminal DUTs, only PSU1 is needed and PSU2 can be ignored. If negative voltages are required at the DUT terminals, the respective PSU terminals are connected with inverted polarity.

Tests are run using the `curvetrace` program. `curvetrace` tests the DUT by varying the voltages $U_1$ and $U_2$ at the PSU terminals, and by reading the corresponding currents $I_1$ and $I_2$. The results are shown on the screen and saved in an ASCII data file for further processing.

Here's a photo showing the test setup for a power MosFET using two RND/Korad PSUs:
![alt text](https://github.com/mbrennwa/PyPSUcurvetrace/blob/master/figures/test_power_MosFET_photo.jpg "Power MosFET test setup")

`curvetrace` provides different methods to control the DUT temperature during the test:
1. `curvetrace` may insert idle periods in between the individual readings, or a "pre-heat" period before starting the test. During these periods, the voltages $U_{1,2}$ and currents $I_{1,2}$ are controlled such that the DUT operates at predefined ``idle'' conditions until the DUT is at thermal equilibrium.
2. `curvetrace` can actively control the temperature of the DUT using a heater block equipped with a heater element and temperature sensor (see below).

`curvetrace` also offers some special operation modes:
* "quick": run "pre-heat" and measure the DUT operating conditions at the idle conditions only, skip curve tracing (may be useful for simple matching of parts based on static idle operating conditions)
* "batch": sequential measurement of parts using the same DUT configuration

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
* If a heater block is used: wait until the DUT has attained the specified temperature.
* The voltages are stepped in two nested loops. Voltage $U_1$ is varied in the inner loop, $U_2$ is varied in the outer loop.
* The measured data are shown on the screen and saved to the data file.
7. Once the test is completed, turn off the PSUs.

### Details
* For each step of the test procedure (measurement, idle, or pre-heat), `curvetrace` sets the voltages at the PSUs according to voltage values requested for this step. The current values of the PSUs are set to the minima of the current and power limits of the DUT and the PSUs at the given test voltages. If the currents established by the DUT are less than the current limits set at the PSUs, the PSUs will operate in "voltage limiting" mode, so that the voltage values required for this test step will be present at the DUT terminals. If the currents established by the DUT reach the current limits set at the PSUs, it is the task of the PSUs to avoid the currents from exceeding the limits by switching to "current limiting" mode, lowering the voltage values applied to the DUT. `curvetrace` reports the occurrence of "current limiting" mode in the data output using "Current Limit" flags.
* Once the inner loop (iteration of $U_1$ steps) reaches a point where either $I_1$ or $I_2$ run into the current or power limits of the DUT or the PSUs, `curvetrace` stops the $U_1$ iterations of the inner loop and returns to the next $U_2$ iteration of the outer loop.
* Once a test voltage has been programmed at a PSU for a DUT measurement, `curvetrace` reads the voltage at the PSU terminals and waits for stabilisation of the read-back output voltage at the set point before continuing. This ensures that measurements are taken only after the voltages applied to the DUT have stabilised at the requested values.
* Some PSU types provide unreliable readings of the voltage or current values if the readings are taken too early after programming a new set point. To improve the reliability of the data obtains from such PSUs, `curvetrace` can be configured to take repeated readings with short idle periods in between. Readings are taken continuously until a specified number of consecutive readings are consistent within the readback resolution of the PSU, and the mean of those readings is returned as the measurement result. This method helps achieving stable, low-noise readings. For configuration of this feature, see the "PSU configuration file" section below.

### Currently supported power supply types:
* Voltcraft PPS
* Korad / RND (confirmed: models KA3005P and KWR103, other models not tested)
* BK Precision (confirmed: model BK9185B, 9120A, other models not tested)

Power supply types on the radar for future support:
* Units with a SCPI interface

## Data plotting
The `curveplot` program allows high-quality plotting of the test data. The `curveplot` documentation can be accessed by executing `curveplot --help`.


## Software installation and configuration
* Download the code from the GitHub repository, either using `git`, `svn` or as a `ZIP` archive.
I like SVN (subversion):
```
svn co https://github.com/mbrennwa/PyPSUcurvetrace.git/trunk path/on/your/computer/to/PyPSUcurvetrace
```
* Install the required Python-3 packages, either using `pip3` or the package manager of your operating system:
    * Some general purpose packages: `serial`, `matplotlib`, `numpy`, `logging`
    * For RIDEN power supplies: `minimalmodbus`
    * Optional (if using a heaterblock): `simple_pid` and `pydigitemp`

* Connect your PSUs to the USB or serial ports of your computer and determine their serial port interfaces on your system.
On Linux:
```
ls /dev/serial/by-id
```
* Copy the `config_PSU_TEMPLATE.txt` file to `config.txt`. Modify the file to reflect the details of the USB/serial interfaces of your your PSUs. See "Notes" section for further information on the PSU configuration file.
* *NOTE:* By default, most Voltcraft units use the same serial device ID. Therefore, it is not possible to access more than one PSU unit via `/dev/serial/by-id/`. If you want to use more than one PSU unit, you will need to modify the device IDs of the serial interfaces so that they are different from each other. See "Notes" section below for details.
* Make sure your user account has permissions to access the serial ports of the PSU units. See "Notes" section below.
* Optional: configure the heater block (see below).

## Using the software
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

## Heater block for temperature control of the DUT (optional)
Documentation for the heater block is under construction.

In the meantime, here's a diagram and a photo of a temperature controlled heater block using power resistors as heaters and a Maxim DS18B20 temperature sensor:
![alt text](https://github.com/mbrennwa/PyPSUcurvetrace/blob/master/figures/heaterblock.png "Heater block diagram")
![alt text](https://github.com/mbrennwa/PyPSUcurvetrace/blob/master/figures/heaterblock_photo.jpg "Heater block photo")

### Heater block design
UNDER CONSTRUCTION

### Software configuration
UNDER CONSTRUCTION

## Examples

### IRFP150 N-channel power mosfet
This example shows curve traces obtained from an IRFP150 N-channel power mosfet (drain current I<sub>D</sub> vs. drain-source voltage V<sub>DS</sub>, measured at different gate-source voltages V<sub>GS</sub>). The IRFP150 pins and PSU outputs were connected according to the above diagram.
* DUT source pin to the negative terminals of PSU1 and PSU2 (joined together)
* DUT drain pin to the positive terminal of PSU1
* DUT gate pin to the positive terminal of PSU2. A gate stopper resistor was used to avoid oscillation.
The power limit for the test was set to 100 W. The curves were recorded at fixed temperatures of 30°C, 50°C and 70°C using a heater block for temperature control (see photo above).
![alt text](https://github.com/mbrennwa/PyPSUcurvetrace/blob/master/figures/IRFP150_curves_heaterblock.png "IRFP150 curves at 30°C, 50°C and 70°C")


### 2SJ79 P-channel mosfet
This example shows curve traces obtained from an 2SJ79 P-channel mosfet (drain current I<sub>D</sub> vs. drain-source voltage V<sub>DS</sub>, measured at different gate-source voltages V<sub>GS</sub>). The 2SJ79 was connected in the same way as the IRFP150 in the previous example, but with the polarity of the PSU terminals inverted to obtain negative test voltages:
* DUT source pin to the positive terminals of PSU1 and PSU2 (joined together)
* DUT drain pin to the negative terminal of PSU1
* DUT gate pin to the negative terminal of PSU2. A gate stopper resistor was used to avoid oscillation.
![alt text](https://github.com/mbrennwa/PyPSUcurvetrace/blob/master/figures/2SJ79_curves.png "2SJ79 curves")


### BC550C BJT/NPN transistor
This example shows curve traces obtained from a BC550C BJT/NPN power transistor (emitter current vs. collector-emitter voltage, measured at different base currents). The BC550 pins and PSU outputs were connected according to the above diagram.
* DUT collector pin to the positive terminal of PSU1
* DUT emitter pin to the negative terminals of PSU1 and PSU2 (joined together)
* DUT base pin to the positive terminal of PSU2 using a base resistor of $R_2$ = 100 kOhm
The power limit for the test was set to 500 mW. The curves were recorded at a fixed temperature of 30°C using a heater block for temperature control (see photo above).

While it would be convenient to use the $I_2$ readings from PSU2 for the BJT base current, the resolution of of these readings tends to be insufficient. Instead, the voltage drop across the base resistor $R_2$ is used to determine the base current. With Ohm's law and $V_{BE}$ = 0.65V, the base current is $I_B = (U_2 - V_{BE}) / R_2$. This $I_B$ calculation is done automatically by the `curveplot` program using the `--bjtvbe 0.65` option.
![alt text](https://github.com/mbrennwa/PyPSUcurvetrace/blob/master/figures/BC550C.png "BC550 curves at 30°C")


### NJW0281G BJT/NPN power transistor
This example shows curve traces obtained from a NJW0281G BJT/NPN power transistor (emitter current vs. collector-emitter voltage, measured at different base currents). The NJW0281G set up and data analysis was analogous as in the BC550 example, using the `--bjtvbe 0.7` option with the `curveplot` program.
![alt text](https://github.com/mbrennwa/PyPSUcurvetrace/blob/master/figures/NJW0281G.png "NJW0281G curves at 50°C")


### 6C33C power triode
This example shows curve traces obtained from an 6C33C power triode (anode current vs. anode-cathode voltage, measured at different negative grid-cathode voltages V<sub>GS</sub>). The 6C33C was connected as follows
* DUT anode pin to the positive terminals of PSU1
* DUT cathode pin to the negative terminal of PSU1 and positive terminal of PSU2 (joined together)
* DUT gate pin to the negative terminal of PSU2.
For this test, only one high-voltage power supply (PSU1) was available. The second power supply (PSU2) was therefore configured as a 90 V PSU made up by a series connection of a 30 V PSU and a 60 V PSU (see below for configuration of such a series combination).

![alt text](https://github.com/mbrennwa/PyPSUcurvetrace/blob/master/figures/6C33C_curves.png "6C33C curves")


## Notes

### Configuration file
The configuration file `config.txt` contains the configuration details of your power supplies (PSUs) and, optionally, also the heaterblock (see below). Take a look at the `config.txt` for details of the file format. There are separate sections for PSU1 and PSU2. Each section contains the following fields:
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

### DUT/Test configuration file
Instead of entering the test parameters manually, the DUT/test parameters can be loaded from a file containing the ranges and step sizes of the test voltages and currents, power limits, etc.

Documentation of the DUT/test configuration file is under constrution! In the meantime, take a look at the example files in the `examples` directory...

### Set user permissions to access serial ports (Linux)
To allow accessing the serial ports, add your username to the `dialout` group. For example, if your user account is `johndoe`, execute the following command:
```
sudo adduser johndoe dialout
```
Then log out and log in again to the user account `johndoe` for this to take effect.

### Modify serial device IDs of the Voltcraft PPS power supplies
In their stock condition, the Silabs CP2102 USB/serial interfaces of the Voltcraft PPS power supplies all use the same ID. The serial interfaces of multiple PPS units connected to the same computer therefore show up at the same file node under /dev/serial/by-id/ (usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0 or similar). In order to simultaneously use more than one PPS unit, the serial interface IDs therefore need to be reconfigured to use unique IDs. This is achieved using the `cp210x-cfg` program:

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
