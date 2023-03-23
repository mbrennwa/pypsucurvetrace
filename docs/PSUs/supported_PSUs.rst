.. include:: ../symbols.rst

.. _supported_PSUs:

************************
Supported power supplies
************************

|pypsucurvetrace| has built-in support for different PSU models. Support for other PSUs can be added on request.

Choosing suitable PSU models for your curve-tracing setup will mainly depend on the voltage and current ranges as well as the set and readback resolution required for your DUT tests:

   * Testing power transistors requires a high-power PSU that can output 100 W or more, while a data resolution of 10 mV and 1-10 mA may be more than sufficient.
   * Testing small-signal transistors requires a high-resolution PSU that can set and read voltages and currents at small increments of about 10-100 μV and 10-100 μA, while the power will be 1 W or less.
   * Testing vacuum tubes also benefits from good low-current resolution, but typically requires high-voltage PSUs (or multiple PSUs connected in series).

The list below describes the PSU models that are supported by |pypsucurvetrace|, and how to configure them in the |PSU_configfile| file.


BK Precision
------------
|pypsucurvetrace| supports the BK Precision 9120A and 9185B models, which both provide 0.01 mA current readback resolution. The 9120A is very suitable for testing small-signal transistors, because it provides 0.1 mV voltage readback resolution with a max voltage of 32 V. The 9185B is suitable for high-voltage devices like electron tubes, because it provides a maximum output voltage of 610 V (with 0.3 V voltage readback resolution).

Configuration of the 9120A in |PSU_configfile|::

   TYPE = BK
   
Configuration of the 9185B in |PSU_configfile|:

   * For high voltage range (up to 610 V, max. current 350 mA)::
   
      TYPE = BK9185B_HIGH
   
   * For low voltage range (up to 400 V, max. current 500 mA)::
   
      TYPE = BK9185B_LOW


Korad / RND
-----------
Korad make cost-effective power supplies which make for a flexible all-purpose test setup. The Korad PSUs are sometimes also available from RND brand.

|pypsucurvetrace| has built-in support for the following models:

   * Tested / confirmed: KA3005P, KWR103
   * Untested / unconfirmed: KA3003P, KD3005P, KA3010P, KA6002P, KA6003P, KA6005P, KD6005P
   
Configuration in |PSU_configfile|::

   TYPE = KORAD


Riden / Ruiden
--------------
Riden / Ruiden offer power supply modules and accessories that allow building very cost-effective power-supply units with high power output and, at the same time, good voltage and current resolution.

|pypsucurvetrace| has built-in support for the following models:

   * Tested / confirmed: RD6006P, RD6012P
   * Untested / unconfirmed: RD6006, RD6012   
   
Configuration in |PSU_configfile|::

   TYPE = RIDEN
   
The RD6012P unit needs special configuration to select the current range and resolution:

   * For 6 A current range and 0.1 mA resolution::
   
      TYPE = RIDEN_6A
   
   * For 12 A current range and 1 mA resolution::
   
      TYPE = RIDEN_12A


Saluki / Maynuo
---------------
The Saluki / Maynuo PSUs are designed for testing and lab work. They are more expensive than some of the other products on this page, but some of their specs exceed those of the more cost-effective units. In particular, the Saluki SPS831 / Maynuo M8831 offers high readback resolution of 0.1 mV and 1 µA, which makes this PSU unit very suitable for testing of low-power duts.

|pypsucurvetrace| has built-in support for the following models:

   * Tested / confirmed: SPS831/M8831
   * Untested / unconfirmed: SPS811/M8811, SPS812/M8812, SPS813/MM813
   
Configuration in |PSU_configfile|::

   TYPE = SALUKI


Voltcraft PPS
-------------
The Voltcraft PPS models have been around for a long time and have served as cost-effective general-purpose PSUs on many work benches. They were used in the first steps in the development of |pypsucurvetrace|.

|pypsucurvetrace| has built-in support for the following models:

   * Tested / confirmed: PPS11360, PPS16005, PPS11810
   * Untested / unconfirmed: PPS11603, PPS13610, PPS11815

Configuration in |PSU_configfile|::

   TYPE = VOLTCRAFT


The Voltcraft PPS power supplies use a Silabs CP2102 USB/serial interface. In stock condition, the Silabs interface of all Voltcraft PPS power supplies always use the same ID. If your setup involves multiplie Voltcraft PPS units, their serial interfaces therefore show up at the same virtual file node under ``/dev/serial/by-id/`` (``usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0`` or similar). In order to simultaneously use more than one PPS unit, you may use the virtual file nodes under ``/dev/serial/by-path/`` instead. However, you may also reconfigure the Silabs interfaces to use unique IDs. This using the ``cp210x-cfg`` program:

* Download the `cp210x-cfg` code::

   svn co https://github.com/DiUS/cp210x-cfg.git
   

* Install USB library stuff needed to compile the `cp210x-cfg` code::

   sudo apt install libusb-1.0-0-dev 


* Compile the `cp210x-cfg` program::

   cd path/to/cp210x-cfg/
   make

* Display HELP information for `cp210x-cfg`, and make *sure* you understand how the program works::

   ./cp210x-cfg -h

* Make sure only one Silabs CP210x interface is connected (the PPS unit one you want to reconfigure), then show its information::

   ./cp210x-cfg

* Change the serial ID of the device (don't mess this up!)::

   ./cp210x-cfg -S 0002

* Plug in the other PPS device and make sure that both serial interfaces now show up separately at `/dev/serial/by_id`::

   ls /dev/serial/by-id/
   usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0
   usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0002-if00-port0
