********
Overview
********

In short, ``pypsucurvetrace`` is a curve-tracer software. It uses programmable power supplies (PSUs) to apply prescribed voltages to a device under test (DUT), and records the resulting currents.

For two-terminal DUTs like resistors or diodes, a single PSU is sufficient. For three-terminal DUTs like transistors (BJTs, FETs, etc.) or vacuum tubes, two PSUs are required (a single PSU box with two separate programmable outputs would also work). ``pypsucurvetrace`` also allows controlling the temperature of the DUT during curve tracing using a heater block. Such a heater block requires an additional PSU for controlled heating.


INCLUDE SCHEMATIC HERE, AND EXPLAIN THE BASICS


Using ``pypsucurvetrace``
-------------------------
The ``pypsucurvetrace`` package provides the following command-line programs:

* ``curvetrace`` is the main program to acquire I/V curve data. See ``curvetrace`` manual for details.
* ``curveplot`` is a helper program to plot curve data. See ``curveplot`` manual for details.
* ``curveprocess`` is a helper program to determine characteristic parameters from curve data. See ``curveprocess`` manual for details.
