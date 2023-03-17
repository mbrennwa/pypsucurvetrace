.. _heaterblock:

************
Heater Block
************

The |curvetrace| program allows controlling the temperature of the DUT during curve tracing. To this end, the DUT is clamped onto a large metal block equipped with a heater element and a temperature sensor. The heater block temperature is controlled by the |curvetrace| program by reading the temperature sensor and adjusting the power of the heater element.

* The thermal inertia of the metal block should be much larger than that of the DUT to allow tight control of the DUT temperature by the heater block. A large block of copper is recommended, which exhibits a large specific heat capacity and thermal conductance.
* A power resistor (or an array of several resistors) is used as heater element. The resistor is powered by power supply controlled by the |curvetrace| program (see :ref:`supported_PSUs` for supported PSUs). The heating power from the resistors and PSU should match the heat capacity of the heater block
* A Maxim DS18B20 digital temperature sensor is used to read the heater block temperature. The 1-Wire bus of the DS18B20 is connected to the computer using a USB-TTL cable (for example FTDI TTL-232R-RPI).

See :ref:`examples_curvetrace_heaterblock` for an example of such a heater block.

The configuration of the heaterblock for the |curvetrace| program is specified in the 


In the meantime, here's a diagram and a photo of a temperature controlled heater block using power resistors as heaters and a Maxim DS18B20 temperature sensor:

.. image:: heaterblock_diagram.png
  :width: 658
  :alt: Heater block diagram


.. image:: heaterblock_photo.jpg
  :width: 658
  :alt: Heater block photo
