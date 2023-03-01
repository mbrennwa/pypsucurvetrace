.. _examples:

Examples
========

.. autosummary::
   :toctree: generated

This chapter presents a number of step-by-step examples to introduce new users to the |pypsucurvetrace| tools. A working installation of the |pypsucurvetrace| software is assumed (see :ref:`installation`).



STRUCTURE: SECTIONS |curvetrace| (incl. PSU config, DUT config, connections setups for pos/negative parts, FETs, BJTs, tubes), |curveplot|, |curveprocess|, |curvematch|, Heaterblock

    * Setup examples (PSUs, heaterblock)
    * Application examples (different DUT types, curve plotting, parameter extraction, matching,...)
    
    
    
.. _examples_curvetrace:

|curvetrace|
--------------

Curve tracing an N-channel FET
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This first example demonstrates test configurations for the PSUs and the DUT (an N-channel FET), and the curvetracing process itself.

``pypsucurvetrace_config.txt`` configuration file needs to be set up following the description in :ref:`curvetrace_PSUconfig`. The PSU1 unit used in this example is a Riden 6012P, which will be used in it's low-current / high-resolution mode. PSU2 is a Riden 6006P (see :ref:`supported_PSUs` for details on these PSUs). The ``pypsucurvetrace_config.txt`` file needs to be created in the home directory and might look like this:::

   [PSU1]
   TYPE    = RIDEN_6A
   COMPORT = /dev/serial/by-path/pci-0000:00:14.0-usb-0:2.4.3:1.0-port0

   [PSU2]
   TYPE    = RIDEN
   COMPORT = /dev/serial/by-path/pci-0000:00:14.0-usb-0:2.4.2:1.0-port0

The easiest method to determine the correct ``COMPORT`` settings for PSU1 is to disconnect all serial interfaces except PSU1, and the list the content of the ``/dev/serial/by-path/`` directory. Then repeat with PSU2.

The DUT considered in this example is a 2SK2013 N-channel FET. The PSU terminals are connected to the DUT pins following the schematic in :ref:`curvetrace`, whereby PSU1 is used with normal polarity and PSU2 with reversed polarity:

   * PSU1-red to Drain pin
   * PSU1-black to Source pin and to PSU2-red --> SOURCE + PSU2-RED
   * PSU2-red to Gate pin
   * PSU2-black to PSU1-black
   
The test parameters for the 2SK2013 are defined by creating a ``2SK2013_test.txt`` file containing the following parameters (see also :ref:`curvetrace_DUTconfig`):::

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
