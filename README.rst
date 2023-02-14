###############
pypsucurvetrace
###############
`pypsucurvetrace` is a *curve tracer*.

More specifically, `pypsucurvetrace` is a software toolbox which uses programmable power supplies (PSUs) for I/V curve tracing of electronic devices. `pypsucurvetrace` is written in Python 3. `pypsucurvetrace` is developed and tested on Linux, but should run on other systems, too.

***********************
Getting pypsucurvetrace
***********************

=============
Prerequisites
=============
The installation procedures described below use the Python package manager ``pipx``. Depending on your installation method (see below), you may also need ``git``. To install these tools on Debian, Ubuntu or similar Linux distros, just run the following command:
	sudo apt install pipx git


Installing, upgrading, and uninstalling
---------------------------------------
You can get `pypsucurvetrace` from it's [GitHub repository](https://github.com/mbrennwa/pypsucurvetrace).

To download and install `pypsucurvetrace` in one single command:
	pipx install git+https://github.com/mbrennwa/pypsucurvetrace

To upgrade `pypsucurvetrace`:
	pipx upgrade pypsucurvetrace

You can also download the `pypsucurvetrace` code separately and then install from the local copy:
	pipx install path/to/pypsucurvetrace

To uninstall `pypsucurvetrace`:
	pipx uninstall pypsucurvetrace

## Usage
The pypsucurvetrace package provides the following command-line programs:
* `curvetrace` is the main program to measure the curve data
* `curveplot` is a helper program to plot curve data
* `curveprocess` is a helper program to determine characteristic parameters from curve data

See the MANUAL file for full documentation.

## License
See the LICENSE file.
