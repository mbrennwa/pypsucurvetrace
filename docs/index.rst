``pypsucurvetrace`` curve tracer
================================

``pypsucurvetrace`` is a software toolbox for «curve tracing» of electronic devices like transistors or vacuum tubes. It uses standard off-the-shelf programmable power supplies (PSUs) to apply different voltages to the device under test (DUT) and to determine the corresponding currents flowing through the DUT.

``pypsucurvetrace`` provides the following command-line tools:

* ``curvetrace`` controls the PSUs and records the «curve data» of the DUT and saves them to a data file. The ``curvetrace`` program can also control the DUT temperature during curve tracing using an optional heater block.
* ``curveplot`` produces high-quality plots of the curve data.
* ``curveprocess`` determines characteristic DUT parameters from the curve data (operating points, gain, output conductance).

The ``pypsucurvetrace`` tools are written in Python 3 and will therefore work on all computers running a modern operating system.

Contents
--------

.. toctree::
   :maxdepth: 1

   installation/installation
   curvetrace/curvetrace
   curveplot/curveplot
   curveprocess/curveprocess
   PSUs/supported_PSUs
   heaterblock/heaterblock
   examples/examples
   
.. note::

   * ``pypsucurvetrace`` is free software and uses the GPL-3 license (see LICENSE.txt or http://www.gnu.org/licenses).

   * Report issues and bugs `here <http://github.com/mbrennwa/pypsucurvetrace/issues>`_ 

   * `Discussion thread <https://www.diyaudio.com/community/threads/idea-for-power-transistor-curve-tracer-good-or-not.344199>`_ about curve tracing with ``pypsucurvetrace``.

   * The ``pypsucurvetrace`` code and this documentation are under construction, and are managed `at GitHub <http://github.com/mbrennwa/pypsucurvetrace>`_.
