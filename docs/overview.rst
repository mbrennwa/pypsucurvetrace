********
Overview
********


``pypsucurvetrace`` is a software toolbox for I/V curve tracing of electronic devices. ``pypsucurvetrace`` uses programmable power supplies to determine curves of currents flowing through the device as a function of different voltages applied to the device. 

* ``pypsucurvetrace`` is free software and uses the GPL-3 license (see LICENSE.txt or http://www.gnu.org/licenses).

* ``pypsucurvetrace`` is written in Python 3. It is developed and tested on Linux, but should run on other systems, too. The source code is hosted and managed `at GitHub <http://github.com/mbrennwa/pypsucurvetrace>`_.

* Report issues and bugs `here <http://github.com/mbrennwa/pypsucurvetrace/issues>`_ 

* Discussion thread about curve tracing with ``pypsucurvetrace`` `here <https://www.diyaudio.com/community/threads/idea-for-power-transistor-curve-tracer-good-or-not.344199>`_ 









``pypsucurvetrace`` uses programmable power supplies to apply different voltages to an electronic device and to determine the currents flowing through the device as a function of the voltages applied (the «curve data»). ``pypsucurvetrace`` also provides tools to process the data and to plot the «curves» of these data.

``pypsucurvetrace`` is written in Python 3. It is developed and tested on Linux, but should run on other systems, too. The source code is hosted and managed at https://github.com/mbrennwa/pypsucurvetrace.

There is also a discussion thread about curve tracing with ``pypsucurvetrace`` at https://www.diyaudio.com/community/threads/idea-for-power-transistor-curve-tracer-good-or-not.344199.

``pypsucurvetrace`` is free software and uses the GPL-3 license (see LICENSE.txt or http://www.gnu.org/licenses).


The ``pypsucurvetrace`` package provides the following command-line programs:

* ``curvetrace`` is the main program to acquire curve data. See ``curvetrace`` manual for details.
* ``curveplot`` is a helper program to plot curve data. See ``curveplot`` manual for details.
* ``curveprocess`` is a helper program to determine characteristic parameters from curve data. See ``curveprocess`` manual for details.
