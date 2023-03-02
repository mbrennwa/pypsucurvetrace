.. include:: ../symbols.rst

.. _examples:

Examples
========

.. autosummary::
   :toctree: generated

This chapter is a modular tutorial built around various examples of how to use the |pypsucurvetrace| tools. It is assumed that you have the |pypsucurvetrace| software installed on your computer (see :ref:`installation` for details).


.. _examples_curvetrace:

|curvetrace|
------------

Configuring the PSUs
^^^^^^^^^^^^^^^^^^^^
To use the |curvetrace| program, you need to setup the PSU configuration file (see :ref:`curvetrace_PSUconfig`). It is assumed that PSU1 unit is a Riden 6012P operating in it's low-current / high-resolution mode, while PSU2 is a Riden 6006P (see :ref:`supported_PSUs`). These PSUs will be useful for testing a wide range of differen DUT types.

The simplest method to determine the ``COMPORT`` for PSU1 on Linux is to disconnect all serial interfaces except PSU1, and then list the virtual file representing the PSU1 serial port in the ``/dev/serial/by-path/`` directory. Repeat for PSU2.

Create the ``pypsucurvetrace_config.txt`` file in your home directory and then enter the following parameters (your ``COMPORT`` settings will be different):::

   [PSU1]
   TYPE    = RIDEN_6A
   COMPORT = /dev/serial/by-path/pci-0000:00:14.0-usb-0:2.4.3:1.0-port0

   [PSU2]
   TYPE    = RIDEN
   COMPORT = /dev/serial/by-path/pci-0000:00:14.0-usb-0:2.4.2:1.0-port0

This minimal PSU configuration file contains all information for the |curvetrace| program to establish the communication with PSU1 and PSU2.



Curve tracing a low-power N-channel FET
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This first example uses the PSU configuration from above to demonstrate the curve tracing of a J112 N-channel jFET.

Connect the PSU terminals to the J112 pins following the schematic in :ref:`curvetrace` (with PSU1 at normal polarity, and PSU2 reversed):

   * PSU1-red to the Drain pin
   * PSU1-black to the Source pin and to PSU2-red
   * PSU2-red to PSU1-black
   * PSU2-black to a grid-stopper resistor at the Gate pin (approximately 1 k|Ohm|)
   
The test parameters for the J112 are defined by creating a ``J112_config.txt`` file containing the following parameters (see also :ref:`curvetrace_DUTconfig`):::

   [PSU1]
   POLARITY = 1
   VSTART = 0
   VEND   = 15
   VSTEP  = 1
   IMAX   = 0.05
   PMAX   = 0.25
   VIDLE  = 7.5
   IIDLE  = 0.02

   [PSU2]
   POLARITY = -1
   VSTART = 0.0
   VEND   = 3.5
   VSTEP  = 0.5
   IMAX   = 1
   PMAX   = 1
   VIDLE     = 5.0
   VIDLE_MIN = 0.0
   VIDLE_MAX = 5.0
   IDLE_GM   = -0.01
   IIDLE     = 1

   [EXTRA]
   IDLESECS    = 0
   PREHEATSECS = 20

To start the curve tracing, execute the following command:

.. code-block:: console
   curvetrace -c J112_config.txt
   
The |curvetrace| program will connect the PSUs, configure the test parameters, and ask you for a file name to save the DUT test data. Once everything is ready, the |curvetrace| program will start the pre-heat process by setting |U1| to the PSU1-``VIDLE`` value and adjust |U2| until |I1| attains the PSU1-``IIDLE`` value. After 20 seconds of pre-heat is stopped, and the curve tracing starts. |U2| is set to 0.0 V, and |U1| is stepped from 0-15 V in 1 V steps. This is repeated for |U2| = -0.5 V, -1.0 V, ... , and -3.5 V. At each step, |U1|, |I1|, |U2|, and |I2| are measured and saved to the data file. The ``curvetrace`` program shows a live plot of the curve data during the measurement.

.. image:: curvetrace_J112.png
  :width: 658
  :alt: ``curvetrace`` example with a J112 jFET


Curve tracing a low-power NPN BJT
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

EXAMPLE WITH BC550, SHOWING HOW TO USE R2 TO CONTROL THE BASE CURRENT



Curve tracing a power FET
^^^^^^^^^^^^^^^^^^^^^^^^^

EXAMPLE WITH IRF150 OR SIMILAR ON A HEATSINK, WITH/WITHOUT TEMPERATURE CONTROL


Curve tracing a vacuum tube
^^^^^^^^^^^^^^^^^^^^^^^^^^^

EXAMPLE WITH VACUUM TUBE (TRIODE, OR PENTODE IN TRIODE CONNECTION), USING HIGH-VOLTAGE PSU (SHOW THE PSU CONFIG), AND AN EXTERNAL HEATER SUPPLY, MAYBE ALSO 


Batch mode
^^^^^^^^^^

EXAMPLE TO ILLUSTRATE BATCH MODE (FOR LATER USE IN MATCHING EXAMPLE)


   
   
.. _examples_curveplot:

|curveplot|
--------------

UNDER CONSTRUCTION


.. _examples_curveprocess:

|curveprocess|
--------------

UNDER CONSTRUCTION


.. _examples_curvematch:

|curvematch|
--------------

UNDER CONSTRUCTION
