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
   
The test parameters for the 2SK2013 are defined by creating a ``2SK2013_config.txt`` file containing the following parameters (see also :ref:`curvetrace_DUTconfig`):::

   [PSU1]
   POLARITY = 1
   VSTART = 0
   VEND   = 20
   VSTEP  = 0.5
   IMAX   = 1.0
   PMAX   = 25
   VIDLE  = 15
   IIDLE  = 0.3
   
   [PSU2]
   POLARITY  = 1
   VSTART    = 1.75
   VEND      = 4.0
   VSTEP     = 0.25
   IMAX      = 1
   PMAX      = 5
   VIDLE     = 3.0
   VIDLE_MIN = 0.5
   VIDLE_MAX = 4.0
   IDLE_GM   = 1
   IIDLE     = 1
   
   [EXTRA]
   IDLESECS    = 0
   PREHEATSECS = 60



Curve tracing an N-channel FET
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This first example uses the PSU configuration from above to demonstrate the curve tracing of a 2SK2013 N-channel FET.

Mount the 2SK2013 on a chunk of metal or a heatsink using a thermal pad for electrical insulation between the FET and the metal. The metal will provide some thermal inertia to prevent large changes of the 2SK2013 temperature during the test.

The PSU terminals are connected to the 2SK2013 pins following the schematic in :ref:`curvetrace`:

   * PSU1-red to the Drain pin
   * PSU1-black to the Source pin and to PSU2-red
   * PSU2-red to a grid-stopper resistor at the Gate pin (approximately 1 k|Ohm|)
   * PSU2-black to PSU1-black
   
The test parameters for the 2SK2013 are defined by creating a ``2SK2013_config.txt`` file containing the following parameters (see also :ref:`curvetrace_DUTconfig`):::

   [PSU1]
   POLARITY = 1
   VSTART = 0
   VEND   = 20
   VSTEP  = 0.5
   IMAX   = 1.0
   PMAX   = 25
   VIDLE  = 15
   IIDLE  = 0.3
   
   [PSU2]
   POLARITY  = 1
   VSTART    = 1.75
   VEND      = 4.0
   VSTEP     = 0.25
   IMAX      = 1
   PMAX      = 5
   VIDLE     = 3.0
   VIDLE_MIN = 0.5
   VIDLE_MAX = 4.0
   IDLE_GM   = 1
   IIDLE     = 1
   
   [EXTRA]
   IDLESECS    = 0
   PREHEATSECS = 60




XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX




If PSU1 is a BK 9185B and PSU2 is a RIDEN 6006P, a minimal ``pypsucurvetrace_config.txt`` file might look like this::

   [PSU1]
   TYPE    = BK
   COMPORT = /dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_508D19126-if00-port0

   [PSU2]
   TYPE    = RIDEN
   COMPORT = /dev/serial/by-id/usb-1a86_USB_Serial-if00-port0
   
   
.. _examples_curvetrace:


|curveplot|
--------------

UNDER CONSTRUCTION


|curveprocess|
--------------

UNDER CONSTRUCTION


|curvematch|
--------------

UNDER CONSTRUCTION
