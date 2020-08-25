.. _transceivers:

Transceivers
============

Implementations
---------------

This package provides only very few implementations for actual I²C
transceivers, i.e. the low level code which controls the I²C hardware:

- :py:class:`~sensirion_i2c_driver.linux_i2c_transceiver.LinuxI2cTransceiver`
  to use an I²C device file provided by the Linux Kernel (e.g. "/dev/i2c-1").
  This transceiver allows to use for example the I²C pins of a Raspberry Pi.

Other implementations are provided in separate Python packages (for
architecture reasons). But to avoid having dependencies from those Packages
to this one just to implement the transceiver interface, we define a backward
compatible API which can be implemented using duck typing, i.e. without
actually inheriting from the common interface. This way we can avoid having
many, often even unnecessary dependencies.


Transceiver API
---------------

Each transceiver object must provide the constant ``API_VERSION`` to indicate
what API version it implements. Every other API requirement is documented in
the corresponding transceiver interface, for example
:py:class:`~sensirion_i2c_driver.transceiver_v1.I2cTransceiverV1` for API
version 1.

**Currently supported API versions:**

- v1: :py:class:`~sensirion_i2c_driver.transceiver_v1.I2cTransceiverV1`

This package (in particular the class
:py:class:`~sensirion_i2c_driver.connection.I2cConnection`) supports all API
versions at the same time, so you don't have to worry about the compatibility
between different package versions.
