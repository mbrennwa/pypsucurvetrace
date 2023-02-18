Examples
========

.. autosummary::
   :toctree: generated

SOME EXAMPLES OF CURVE TRACES

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

