.. _examples:

Examples
========

.. autosummary::
   :toctree: generated


UNDER CONSTRUCTION...

STRUCTURE: SECTIONS |curvetrace| (incl. PSU config, DUT config, connections setups for pos/negative parts, FETs, BJTs, tubes), |curveplot|, |curveprocess|, |curvematch|, Heaterblock

    * Setup examples (PSUs, heaterblock)
    * Application examples (different DUT types, curve plotting, parameter extraction, matching,...)
    
    
    
.. _examples_curvetrace:

|curvetrace|
--------------

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
