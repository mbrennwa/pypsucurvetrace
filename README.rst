###############
pypsucurvetrace
###############
`pypsucurvetrace` is a *curve tracer*.

More specifically, `pypsucurvetrace` is a software toolbox which uses programmable power supplies (PSUs) to determine curves of current flowing through an electronic device at different voltages applied to the device (I/V curves).

`pypsucurvetrace` is written in Python 3. `pypsucurvetrace` is developed and tested on Linux, but should run on other systems, too. The source code is available at https://github.com/mbrennwa/pypsucurvetrace .

***********************
Getting pypsucurvetrace
***********************


Prerequisites
=============

The installation procedures described below use the Python package manager ``pipx``. Depending on your installation method (see below), you may also need ``git``.

To install these tools on Debian, Ubuntu or similar Linux distros, just run the following command:

.. code-block:: console

   sudo apt install pipx git


Installing, upgrading, and uninstalling
---------------------------------------
To download and install ``pypsucurvetrace`` in one single command:

.. code-block:: console

   pipx install git+https://github.com/mbrennwa/pypsucurvetrace

To upgrade ``pypsucurvetrace``:

.. code-block:: console

   pipx upgrade pypsucurvetrace

You can also download the ``pypsucurvetrace`` code separately and then install from the local copy:

.. code-block:: console

   pipx install path/to/pypsucurvetrace

To uninstall ``pypsucurvetrace``:

.. code-block:: console

   pipx uninstall pypsucurvetrace

Using ``pypsucurvetrace``
-------------------------
The ``pypsucurvetrace`` package provides the following command-line programs:
* ``curvetrace`` is the main program to measure the curve data
* ``curveplot`` is a helper program to plot curve data
* ``curveprocess`` is a helper program to determine characteristic parameters from curve data

See the MANUAL file for full documentation.

License
-------
See the LICENSE file.
