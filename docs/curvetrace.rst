The ``curvetrace`` program
==========================

.. autosummary::
   :toctree: generated

OVERVIEW, SCHEMATIC, SETUP

Configuration
-------------


For two-terminal DUTs like resistors or diodes, a single PSU is sufficient. For three-terminal DUTs like transistors (BJTs, FETs, etc.) or vacuum tubes, two PSUs are required (a single PSU box with two separate programmable outputs would also work). ``pypsucurvetrace`` also allows controlling the temperature of the DUT during curve tracing using a heater block. Such a heater block requires an additional PSU for controlled heating.

