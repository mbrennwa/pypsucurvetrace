# PyPSUcurvetrace
*PyPSUcurvetrace* is a software toolbox for I/V curve tracing of electronic devices using programmable power supplies (PSUs). In short, *PyPSUcurvetrace* is a *curve tracer*.

## Installation
You can get `PyPSUcurvetrace` from it's [GitHub repository](https://github.com/mbrennwa/PyPSUcurvetrace).

The installation uses the Python-3 package manager `pip3`, so make sure this is installed on your machine. For example, on Debian or Ubuntu and similar Linux distros, just run `sudo apt install pip` so install `pip3`.

You can download and install `PyPSUcurvetrace` in one single command (you need `git` installed on your machine):
```bash
pip3 install --upgrade git+https://github.com/mbrennwa/PyPSUcurvetrace
```

You can also download the `PyPSUcurvetrace` code separately and then install from the local copy:
```bash
pip3 install --upgrade path/to/PyPSUcurvetrace
```

To uninstall `PyPSUcurvetrace`:
```bash
pip3 uninstall PyPSUcurvetrace
```

## Usage
The PyPSUcurvetrace package provides the following command-line programs:
* `curvetrace` is the main program to measure the curve data
* `curveplot` is a helper program to plot curve data
* `curveprocess` is a helper program to determine characteristic parameters from curve data

See the MANUAL file for full documentation.

## License
See the LICENSE file.
