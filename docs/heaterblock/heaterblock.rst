.. _heaterblock:

.. include:: ../symbols.rst


************
Heater Block
************

The |curvetrace| program allows controlling the temperature of the DUT during curve tracing. To this end, the DUT is clamped onto a large metal block equipped with heater elements and a temperature sensor. The heater block temperature is controlled by the |curvetrace| program by reading the temperature sensor and adjusting the power of the heater element, as illustrated in the following diagram:

.. image:: heaterblock_diagram.png
  :width: 658
  :alt: Heater block diagram

* To allow tight control of the DUT temperature by the heater block, its thermal inertia should be much larger than that of the DUT. A large block of copper is recommended, which exhibits a large specific heat capacity and thermal conductance.
* Power resistors are used as heater elements. The resistor array is powered by a PSU, which is controlled by the |curvetrace| program (see :ref:`supported_PSUs` for supported PSUs). The heating power from the resistors and PSU should match the heat capacity of the heater block
* A Maxim DS18B20 digital temperature sensor is used to read the heater block temperature. The 1-Wire bus of the DS18B20 is connected to the computer using a USB-TTL cable (for example FTDI TTL-232R-RPI).
* The temperature control loop is implemented as a `PID controller <https://en.wikipedia.org/wiki/PID_controller>`_ in the |curvetrace| software.

See :ref:`examples_curvetrace_heaterblock` for an example of such a heater block.

The configuration of the heaterblock for the |curvetrace| program is specified in the |PSU_configfile| file by adding a ``[HEATERBLOCK]`` section as follows:::

   [HEATERBLOCK]

   PSU_COMPORT       = ...
   PSU_TYPE          = ...
   TEMPSENS_COMPORT  = ...
   TEMPSENS_TYPE     = ...
   TBUFFER_NUM       = ...
   TBUFFER_INTERVAL  = ...
   NUMSTABLEREAD     = ...
   HEATER_RESISTANCE = ...
   MAX_POWER         = ...
   KP                = ...
   KI                = ...
   KD                = ...

* ``PSU_COMPORT`` and ``PSU_TYPE``: COM port and type of the PSU used for the heaters (see also :ref:`curvetrace_PSUconfig` and :ref:`supported_PSUs` for details).
* ``TEMPSENS_COMPORT``: COM port of the temperature sensor
* ``TEMPSENS_TYPE``: type of temperature sensor. Currently, only ``TEMPSENS_TYPE = DS1820`` is supported.
* ``TBUFFER_NUM``: number of temperature readings to store in memory
* ``TBUFFER_INTERVAL``: time between temperature readings (in seconds)
* ``NUMSTABLEREAD``: number of temperature readings that must be consistent with the target temperature in order to assume temperature conditions (must not be higher than ``TBUFFER_NUM``)
* ``HEATER_RESISTANCE``: resistance of the combined heater resistors (in Ohm)
* ``MAX_POWER``: maximum heating power
* ``KP``, ``KI``, ``KD``: coefficients of the `PID controller <https://en.wikipedia.org/wiki/PID_controller>`_
