.. _supported_PSUs:

************************
Supported power supplies
************************

``pypsucurvetrace`` has built-in support for a number of different PSU models. Choosing suitable PSU models for your curve-tracing setup will mainly depend on the voltage and current ranges as well as the set and readback resolution required for your DUT tests. For example, testing a power transistor may require a high-power PSU that can output several 100~W, while a data resolution of 0.01~V and 0.01~A may be more than sufficient. In contrast, testing a small-signal transistor will require much higher resolution to set and read voltages and currents at small increments of 0.1~mV and 0.1~mA or so, while the power will be 1~W or less. Yet another situation arises with vacuum tubes, which typically require high-voltage PSUs (or several PSUs connected in series).

The list below describes the PSU models that are supported by ``pypsucurvetrace``, and how to configure them in the ``pypsucurvetrace_config.txt`` file.

Korad / RND
-----------
Korad make a number of different cost-effective power supplies which make for a flexible all-purpose test setup. The Korad PSUs are sometimes also available from RND brand.

``pypsucurvetrace`` has built-in support for the following models:

   * Tested / confirmed: KA3005P, KWR103
   * Untested / unconfirmed: KA3003P, KD3005P, KA3010P, KA6002P, KA6003P, KA6005P, KD6005P
   
Configuration in ``pypsucurvetrace_config.txt``::

   TYPE = KORAD


Riden / Ruiden
--------------
Riden / Ruiden offer a number of different power supply modules and accessories that allow building very cost-effective power-supply units with high power output and, at the same time, good voltage and current resolution.

``pypsucurvetrace`` has built-in support for the following models:

   * Tested / confirmed: RD6006P, RD6012P
   * Untested / unconfirmed: RD6006, RD6012   
   
Configuration in ``pypsucurvetrace_config.txt``::

   TYPE = RIDEN
   
The RD6012P unit needs special configuration to select the current range and resolution:

   * For 6 A current range and 0.1 mA resolution::
   
      TYPE = RIDEN_6A
   
   * For 12 A current range and 1 mA resolution::
   
      TYPE = RIDEN_12A


BK Precision
------------
DESCRIBE HERE...

confirmed: model BK9185B, 9120A, other models not tested


Voltcraft PPS
-------------
DESCRIBE HERE...

confirmed: ...

In their stock condition, the Silabs CP2102 USB/serial interfaces of the Voltcraft PPS power supplies all use the same ID. The serial interfaces of multiple PPS units connected to the same computer therefore show up at the same file node under /dev/serial/by-id/ (usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0 or similar). In order to simultaneously use more than one PPS unit, the serial interface IDs therefore need to be reconfigured to use unique IDs. This is achieved using the `cp210x-cfg` program:

* Download the `cp210x-cfg` code:
```
svn co https://github.com/DiUS/cp210x-cfg.git
```

* Install USB library stuff needed to compile the `cp210x-cfg` program:
```
sudo apt install libusb-1.0-0-dev 
```

* Compile the `cp210x-cfg` program:
```
cd path/to/cp210x-cfg/
make
```

* Display HELP information for `cp210x-cfg`, and make *sure* you understand how the program works:
```
./cp210x-cfg -h
```

* Make sure only one Silabs CP210x interface is connected (the PPS unit one you want to reconfigure), then show its information:
```
./cp210x-cfg
```

* Change the serial ID of the device (don't mess this up!):
```
./cp210x-cfg -S 0002
```

* Plug in the other PPS device and make sure that both serial interfaces now show up separately at `/dev/serial/by_id`:
```
ls /dev/serial/by-id/
usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0
usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0002-if00-port0
```
