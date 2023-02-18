.. _supported_PSUs:

************************
Supported power supplies
************************

The list below describes the PSU models that are supported by ``pypsucurvetrace`` and how to configure them for ``pypsucurvetrace``.


Korad / RND
-----------
DESCRIBE HERE...

confirmed: models KA3005P and KWR103, other models not tested)


Riden / Ruiden
--------------
DESCRIBE HERE...

confirmed: ...


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
