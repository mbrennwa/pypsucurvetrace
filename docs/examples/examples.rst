.. include:: ../symbols.rst

.. _examples:

Examples
========

.. autosummary::
   :toctree: generated

This chapter is a modular tutorial built around various examples illustrating the use of the |pypsucurvetrace| tools. It is assumed that you have the |pypsucurvetrace| software installed on your computer (see :ref:`installation` for details).


.. _examples_curvetrace:

Working with the |curvetrace| program
-------------------------------------

Configuring the PSUs
^^^^^^^^^^^^^^^^^^^^
To use the |curvetrace| program, you need to setup the PSU configuration file (see :ref:`curvetrace_PSUconfig`). It is assumed that PSU1 unit is a Riden 6012P operating in it's low-current / high-resolution mode, while PSU2 is a Riden 6006P (see :ref:`supported_PSUs`). These PSUs will be useful for testing a wide range of differen DUT types.

The simplest method to determine the ``COMPORT`` for PSU1 on Linux is to disconnect all serial interfaces except PSU1, and then list the virtual file representing the PSU1 serial port in the ``/dev/serial/by-path/`` directory. Repeat for PSU2.

Create the ``curvetrace_config.txt`` file in your home directory and then enter the following parameters (your ``COMPORT`` settings will be different):::

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

The J112 needs a positive Drain-Source voltage (|U1|) and a negative Gate-Source voltage (|U2|). Therefore, connect PSU1 with positive polarity and PSU2 with negative polarity to the J112 pins following the schematic in :ref:`curvetrace`:

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

Execute the following command to start the curve tracing:

.. code-block:: console

   curvetrace -c J112_config.txt
   
The |curvetrace| program starts communication with the PSUs, configures the test parameters, and asks you for a file name to save the DUT test data. Once everything is ready, the |curvetrace| program runst the pre-heat process by setting |U1| to the PSU1-``VIDLE`` value (7.5 v) and adjust |U2| until |I1| attains the PSU1-``IIDLE`` value of 0.02 A (20 mA). After 20 seconds the pre-heat is stopped (``PREHEATSECS``), and the curve tracing starts. |U2| is set to 0.0 V, and |U1| is stepped from 0-15 V in 1 V steps. This sequence is repeated for |U2| = -0.5 V, -1.0 V, ... , and -3.5 V. At each step, |U1|, |I1|, |U2|, and |I2| are measured and saved to the data file. The ``curvetrace`` program shows a live plot of the curve data during the measurement as shown below.

.. image:: curvetrace_J112.png
  :width: 658
  :alt: ``curvetrace`` example with a J112 jFET


Curve tracing a low-power NPN BJT
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

EXAMPLE WITH BC550, SHOWING HOW TO USE R2 TO CONTROL THE BASE CURRENT

This example demonstrates how to test a bipolar transistor (BJT). In contrast to the previous FET example, the BJT is controlled the the base *current*. Since the base current is typically much smaller than the current measurement resolution of most PSUs, the ``curvetrace`` program uses the |R2| resistor to convert the |U2| voltage to the base current value (see ref:`curvetrace` for details). The conversion relies on the exact |R2| value, which is determined by the max. |U2| output voltage of the PSU2 and the max. |Ib| current required for the test. The max. output voltage of PSU2 (Riden 6006P) is 60 V, and the targeted base current should range up to about 50 μA. With |Ib| = (|U2| - |VBEon|) / |R2|, a suitable value for the test is |R2| = 100 k |Ohm|.

The BC550 needs a positive Collector-Emitter voltage (|U1|) and a positive Base-Emitter voltage (|U2|), so you need to connect the pins as follows:

# - PSU1-RED --> COLLECTOR
# - PSU1-BLK --> EMITTER + PSU2-BLK
# - PUS2-RED --> BASE (VIA 100k RESISTOR)
# - PSU2-BLK --> PSU1-BLK


   * PSU1-red to the Collector pin
   * PSU1-black to the Emitter pin and to PSU2-black
   * PSU2-red to the Base pin via the 100 k|Ohm| |R2| resistor
   * PSU2-black to PSU2-black
   
The test parameters for the BC550 are defined by creating a ``BC550_config.txt`` file containing the following parameters (see also :ref:`curvetrace_DUTconfig`):::

   [PSU1]
   POLARITY = 1
   VSTART = 0
   VEND   = 20
   VSTEP  = 1
   IMAX   = 0.1
   PMAX   = 0.5
   VIDLE  = 5
   IIDLE  = 0.02
   
   [PSU2]
   POLARITY = 1
   VSTART = 0.65
   VEND   = 6.65
   VSTEP  = 0.5
   IMAX   = 0.1
   PMAX   = 1
   VIDLE     = 0.8
   VIDLE_MIN = 0.0
   VIDLE_MAX = 20
   IDLE_GM   = 0.01
   IIDLE     = 1
   
   [EXTRA]
   R2CONTROL = 100000
   IDLESECS    = 2
   PREHEATSECS = 60
   NREP        = 1

Run |curvetrace|:

.. code-block:: console

   curvetrace -c J112_config.txt

The curve tracing works in the same way as in the previous example, with two exceptions. First, the |U2| steps start at 0.65 V, which is the (assumed) |VBEon|-on value of the BC550. Second, there is a 2 second idle time between each reading for re-equilibration of the BC550 temperature before each reading, which reduces the distortion of the curves at higher power levels due to self-heating of the transistor. The following plot shows the BC550 curves measured with and without the 2 s idle time between readings:

.. image:: curvetrace_BC550_selfheating.png
  :width: 658
  :alt: BC550 curves with/without self-heating control

The conversion from |U2| to the base-current is done later during curve plotting and data processing (see also :ref:`examples_curveplot`, :ref:`examples_curveprocess` and :ref:`examples_curvematch`).


Curve tracing a power FET
^^^^^^^^^^^^^^^^^^^^^^^^^

EXAMPLE WITH IRF150 OR SIMILAR ON A HEATSINK, WITH/WITHOUT TEMPERATURE CONTROL


Curve tracing a vacuum tube
^^^^^^^^^^^^^^^^^^^^^^^^^^^

EXAMPLE WITH VACUUM TUBE (TRIODE, OR PENTODE IN TRIODE CONNECTION), USING HIGH-VOLTAGE PSU (SHOW THE PSU CONFIG), AND AN EXTERNAL HEATER SUPPLY, MAYBE ALSO 


Batch mode
^^^^^^^^^^

EXAMPLE TO ILLUSTRATE BATCH MODE (FOR LATER USE IN MATCHING EXAMPLE)


Controlling DUT temperature with a heater block
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

DESCRIBE THE HEATERBLOCK: CONSTRUCTION, CONFIGURATION, PRACTICAL ASPECTS, USAGE EXAMPLE (IRF150 CURVES AT DIFFERENT TEMPERATURES, MAYBE?)


   
   
.. _examples_curveplot:

Working with the |curveplot| program
------------------------------------

UNDER CONSTRUCTION


.. _examples_curveprocess:

Working with the |curveprocess| program
---------------------------------------

UNDER CONSTRUCTION


.. _examples_curvematch:

Working with the |curvematch| program
-------------------------------------

UNDER CONSTRUCTION
