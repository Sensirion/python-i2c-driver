sensirion-i2c-driver
====================

This package contains the base I²C driver for various Sensirion sensors.
It handles low-level things like type conversions, checksum calculation,
error handling etc.


Note
----

Normally you shouldn't use this driver directly - instead you should use the
device-specific driver for your actual device as it provides easy-to-use
commands. But this driver is still useful if you want to transceive raw I²C
frames, or if there is no specific driver available yet for your device.


Installation and Usage
----------------------

The user manual is available at https://sensirion.github.io/python-i2c-driver/.
