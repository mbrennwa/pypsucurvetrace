# PyPSUcurvetrace
`pypsucurvetrace` is a *curve tracer*.

More specifically, `pypsucurvetrace` is a software toolbox which uses programmable power supplies (PSUs) for I/V curve tracing of electronic devices. `pypsucurvetrace` is written in Python 3.

## Installation
You can get `pypsucurvetrace` from it's [GitHub repository](https://github.com/mbrennwa/pypsucurvetrace).

The installation uses the Python-3 package manager `pipx`, so make sure this is installed on your machine. For example, on Debian or Ubuntu and similar Linux distros, just run `sudo apt install pipx` so install `pipx`.

You can download and install `pypsucurvetrace` in one single command (you need `git` installed on your machine):
```bash
pipx install git+https://github.com/mbrennwa/pypsucurvetrace
```

To upgrade `pypsucurvetrace`:
```bash
pipx upgrade git+https://github.com/mbrennwa/pypsucurvetrace
```

You can also download the `pypsucurvetrace` code separately and then install from the local copy:
```bash
pipx install path/to/pypsucurvetrace
```

To uninstall `pypsucurvetrace`:
```bash
pipx uninstall pypsucurvetrace
```

## Usage
The pypsucurvetrace package provides the following command-line programs:
* `curvetrace` is the main program to measure the curve data
* `curveplot` is a helper program to plot curve data
* `curveprocess` is a helper program to determine characteristic parameters from curve data

See the MANUAL file for full documentation.

## License
See the LICENSE file.
