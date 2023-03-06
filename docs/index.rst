.. include:: symbols.rst

|pypsucurvetrace| curve tracer
================================

|pypsucurvetrace| is a software toolbox for «curve tracing» of electronic devices like transistors or vacuum tubes. It uses standard off-the-shelf programmable power supplies (PSUs) to apply predefined voltages to the device under test (DUT) and to determine the corresponding currents flowing through the DUT.


.. grid::

    .. grid-item-card:: Installation
        :link: installation/installation
        :link-type: doc

        How to install the |pypsucurvetrace| software


    .. grid-item-card:: Software User Guide
        :link: overview/userguide
        :link-type: doc

        User guide for the |pypsucurvetrace| tools


    .. grid-item-card:: Hardware Setup
        :link: :ref:`curvetrace_hardwaresetup`
        :link-type: doc

        Hardware setup for curve tracing


.. grid::

    .. grid-item-card:: Tutorial and Examples
        :link: examples/examples
        :link-type: doc

        Tutorial with worked examples
        

    .. grid-item-card:: Contribute
        :link: overview/contribute
        :link-type: doc

        How to contribute to |pypsucurvetrace| or report bugs



|pypsucurvetrace| provides the following command-line tools:

* |curvetrace| controls the PSUs and records the «curve data» of the DUT and saves them to a data file. The |curvetrace| program can also control the DUT temperature during curve tracing using an optional heater block.
* |curveplot| produces high-quality plots of the curve data.
* |curveprocess| determines characteristic DUT parameters from the curve data (operating points, gain, output conductance).
* |curvematch| calculates the «difference between two curve sets» to help finding parts with similar curves (part matching).

The |pypsucurvetrace| tools are written in Python 3 and will therefore work on all computers running a modern operating system.

Contents
--------

.. toctree::
   :maxdepth: 1

   installation/installation
   curvetrace/curvetrace
   curveplot/curveplot
   curveprocess/curveprocess
   curvematch/curvematch
   PSUs/supported_PSUs
   heaterblock/heaterblock
   examples/examples
   
.. note::

   * |pypsucurvetrace| is free software and uses the GPL-3 license (see LICENSE.txt or http://www.gnu.org/licenses).

   * Report issues and bugs `here <http://github.com/mbrennwa/pypsucurvetrace/issues>`_ 

   * `Discussion thread <https://www.diyaudio.com/community/threads/idea-for-power-transistor-curve-tracer-good-or-not.344199>`_ about curve tracing with |pypsucurvetrace|.

   * The |pypsucurvetrace| code and this documentation are under construction, and are managed `at GitHub <http://github.com/mbrennwa/pypsucurvetrace>`_.
