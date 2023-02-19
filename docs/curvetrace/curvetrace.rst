.. _curvetrace:

The ``curvetrace`` program
==========================

.. |U1| replace:: :math:`U_1`
.. |U2| replace:: :math:`U_2`
.. |I1| replace:: :math:`I_1`
.. |I2| replace:: :math:`I_2`
.. |R2| replace:: :math:`R_2`
.. |Ohm| unicode:: U+02126
.. |Vbe| replace:: :math:`V_{\rm BE}`
.. |Ib| replace:: :math:`I_{\rm B}`

.. autosummary::
   :toctree: generated


.. image:: test_setup.png
  :width: 658
  :alt: Schematic of test circuit

The figure shows the circuit used to analyse a device under test (DUT) using two programmable power supplies (PSU1 and PSU2). The ``curvetrace`` program controls the voltages |U1| and |U2| at the terminals of PSU1 and PSU2, and records the currents |I1| and |I2| using the built-in meters of PSU1 and PSU2.

The figure shows a test setup where both |U1| and |U2| are positive, while negative voltages are achieved by reversing the polarity of one or both PSUs.


The resistor |R2| serves multiple purposes:

   * For voltage-controlled DUTs like FETs or vacuum tubes, the resistor prevents high-frequency oscillation at the FET gate or tube grid. An |R2| value of approximately 10\ :sup:`3` |Ohm| is recommended, but the exact value is not critical and will not have an effect on the test results.
   * For current-controlled DUTs like BJTs, the resistor is used to convert the control voltage to the control current |Ib| using Ohm's Law. The voltage drop across |R2| is equal to |U2| - |Vbe|, where |Vbe| is the base-emitter on voltage of the BJT. Therefore, the control current is given by |Ib| = (|U2| - |Vbe|) / |R2|.

The ``curvetrace`` program allows limiting the currents (|I1|, |I2|) and power (|U1| × |I1|, |I2| × |U2|) to prevent overloading the DUT during testing.

The ``curvetrace`` program supports a number of different PSU models. See :ref:`supported_PSUs` for details.

The ``curvetrace`` program allows using a heater block to control the temperature of the DUT during curve tracing. See :ref:`heaterblock` for details.


Test procedure
--------------

The procedure implemented in the ``curvetrace`` program is as follows:

   1. Read the ``pypsucurvetrace_config.txt`` configuration file with the types and serial ports of the PSUs, and then establish the serial connection to the PSUs (see below).
   
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
         * The voltages are stepped in two nested loops. Voltage |U1| is varied in the inner loop, |U2| is varied in the outer loop.
         * The measured data are shown on the screen and saved to the data file.
         
   7. Once the test is completed, turn off the PSUs.


Power supply configuration
--------------------------
The basic configuration required for ``curvetrace`` to work is to specify the PSU models used, and their communication port is connected to the computer. To specify these configurations, create a file ``pypsucurvetrace_config.txt`` and enter the PSU configurations as follows:::

   [PSU1]
   TYPE    = <PSU TYPE OR MODEL>
   COMPORT = <COM PORT>

   [PSU2]
   TYPE    = <PSU TYPE OR MODEL>
   COMPORT = <COM PORT>

* ``TYPE``: the type or model of the PSU. See :ref:`supported_PSUs` for details.
* ``COMPORT``: path of the virtual file corresponding to the serial port of the PSU

For example, if PSU1 is a BK 9185B and PSU2 is a RIDEN 6006P, a minimal ``pypsucurvetrace_config.txt`` file might look like this::

   [PSU1]
   TYPE    = BK
   COMPORT = /dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_508D19126-if00-port0

   [PSU2]
   TYPE    = RIDEN
   COMPORT = /dev/serial/by-id/usb-1a86_USB_Serial-if00-port0

Note that it is possible to connect multiple PSU units in series to each other to accomplish a higher voltage range. Such a series combination of multiple PSU units can be configured as a single PSU object by specifying their `TYPE` and `COMPORT` fields as follows:

* ``TYPE = ( "<type_psu1>" , "<type_psu2>" )``
* ``COMPORT = ( "<comport_psu1>" , "<comport_psu2>" )``

There are further configuration options to improve the the quality of the the PSU data (FULL DOCUMENTATION FOR THESE IS UNDER CONSTRUCTION):

* ``NUMSTABLEREAD``: number of readings that must have identical values in order to accept the reading.
* ``V_SET_CALPOLY``, ``I_SET_CALPOLY``, ``V_READ_CALPOLY`` and ``I_READ_CALPOLY``: coefficients to specify external calibration data to set and read the voltage and current values at the PSU.


Heaterblock configuration
-------------------------
The configuration of the heaterblock is only required if a heater block is used. The heaterblock configuration is also specified in the ``pypsucurvetrace_config.txt`` file. See :ref:`heaterblock` for details.


Running ``curvetrace``
----------------------
The ``curvetrace`` program is invoked from the command line. Full documentation is not yet available in this document, but can be accessed from the ``curvetrace`` program directly:

.. code-block:: console

   curvetrace --help


Examples
--------
UNDER CONSTRUCTION...
