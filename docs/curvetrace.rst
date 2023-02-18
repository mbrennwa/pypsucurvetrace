The ``curvetrace`` program
==========================

.. |U1| replace:: U\ :sub:`1`\ O
.. |U2| replace:: U\ :sub:`2`\ O
.. |I1| replace:: I\ :sub:`1`\ O
.. |I2| replace:: I\ :sub:`2`\ O


.. autosummary::
   :toctree: generated


.. image:: test_setup.png
  :width: 658
  :alt: Schematic of test circuit

The figure shows the circuit used to analyse a device under test (DUT) using two programmable power supplies (PSU1 and PSU2). The ``curvetrace`` program controls the voltages |U1| and |U2| at the terminals of PSU1 and PSU2, and records the currents |I1| and |I2| using the built-in meters of PSU1 and PSU2. The ``curvetrace`` program either asks the user to enter the desired values of |U1| and |U2|, or uses a configuration file with |U1| and |U2| presets required for a specific test. ``curvetrace`` also allows limiting the |I1| and |I2| currents or the power values |U1|×|I1| and |I2|×|U2| to prevent overloading the DUT. The figure shows a test setup where both |U1| and |U2| are positive. ``curvetrace`` also allows using negative voltages by reversing the polarity of the PSUs.

The ``curvetrace`` program supports a number of different PSU models. See :ref:`supported_PSUs` for details.

The ``curvetrace`` program also allows using a heater block to control the temperature of the DUT during curve tracing. See :ref:`heaterblock` for details.


Configuration of the test setup
-------------------------------
The basic configuration required for ``curvetrace`` to work is to specify the PSU models used, and their communication port is connected to the computer. To specify these configurations, create a file `pypsucurvetrace_config.txt` and enter the PSU configurations as follows:::

   [PSU1]
   TYPE    = <PSU TYPE OR MODEL>
   COMPORT = <COM PORT>

   [PSU2]
   TYPE    = <PSU TYPE OR MODEL>
   COMPORT = <COM PORT>

* `COMPORT`: path of the virtual file corresponding to the serial port of the PSU
* `COMMANDSET`: the type or model of the PSU. See :ref:`supported_PSUs` for details.

For example, if PSU1 is a BK 9185B and PSU2 is a RIDEN 6006P, a minimal `pypsucurvetrace_config.txt` file might look like this:::

   [PSU1]
   TYPE    = BK
   COMPORT = /dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_508D19126-if00-port0

   [PSU2]
   TYPE    = RIDEN
   COMPORT = /dev/serial/by-id/usb-1a86_USB_Serial-if00-port0

Note that it is possible to connect multiple PSU units in series to each other to accomplish a higher voltage range. Such a series combination of multiple PSU units can be configured as a single PSU object by specifying their `TYPE` and `COMPORT` fields as follows:

* `TYPE = ( "<commandset_psu1>" , "<commandset_psu2>" )`
* `COMPORT = ( "/dev/serial/by-id/<xxx_psu1>" , "/dev/serial/by-id/<xxx_psu2>" )`
