.. _device_driver_guidelines:

Device Driver Guidelines
========================

To help ensuring consistency between the various I²C device drivers, this page
defines some guidelines how device drivers should be designed. It is highly
recommended to follow these guidelines when creating a new device driver.

Directory Structure
-------------------

It is recommended that each device driver contains (at least) the following
two files:

- ``commands.py``: Containing all I²C command classes (derived from
  :py:class:`~sensirion_i2c_driver.command.I2cCommand`).
- ``device.py``: Containing one device class (derived from
  :py:class:`~sensirion_i2c_driver.device.I2cDevice`) to wrap each command by
  a method.

If a Python package contains drivers for multiple I²C devices, create
(possibly nested) subdirectories for them, for example like that:

.. sourcecode:: none

    sensirion_i2c_sht
        ├── sht2x
        │   ├── commands.py
        │   └── device.py
        ├── sht3x
        │   ├── commands.py
        │   └── device.py
        └── shtc3
            ├── commands.py
            └── device.py


In addition, it's often handy to also add a ``__init__.py`` file to each
directory to re-export the classes so the user doesn't need to care about the
module names (e.g. allow importing ``Sht3xI2cDevice`` instead of
``device.Sht3xI2cDevice``).


Command Base Class
------------------

Within ``commands.py``, there should be a command class added which is then
inherited by each command of the particular device. This is useful to specify
the communication parameters which are common to all commands, for example the
CRC argorithm. This is how such a class could look like:

.. sourcecode:: python

    from sensirion_i2c_driver import SensirionI2cCommand, CrcCalculator

    class Sht3xI2cCmdBase(SensirionI2cCommand):
        def __init__(self, command, tx_data, rx_length, read_delay, timeout,
                     post_processing_time=0.0):
            super(Sht3xI2cCmdBase, self).__init__(
                command=command,
                tx_data=tx_data,
                rx_length=rx_length,
                read_delay=read_delay,
                timeout=timeout,
                crc=CrcCalculator(8, 0x31, 0xFF, 0x00),
                command_bytes=2,
                post_processing_time=post_processing_time,
            )


Command TX/RX Data Types
------------------------

Sometimes it's not easy to decide what type should be passed to the command
constructor (data written to the device) or returned by the
:py:meth:`~sensirion_i2c_driver.command.I2cCommand.interpret_response` method
(data received from the device), respectively what physical unit these values
should have. For example, physical values are often transferred over I²C as
integers with a specific scaling and offset to get suitable resolution, but
humans usually prefer to work with a standard physical unit.

To help deciding how to implement it, here some possible solutions:

Pass-Through Raw Values
^^^^^^^^^^^^^^^^^^^^^^^

This variant is recommended if the value represents no physical unit or has no
offset and scaling.

Examples:

- Measure interval in Milliseconds (e.g. ``5`` represents 5 ms)
- Serial number as a string (no physical unit)

.. sourcecode:: python

    from struct import pack, unpack

    class Sht3xI2cCmdSimpleExample(Sht3xI2cCmdBase):
        def __init__(self, measure_interval_ms, delay_ms):
            super(Sht3xI2cCmdSimpleExample, self).__init__(
                tx_data=pack(">HH", measure_interval_ms, delay_ms),
                rx_length=4, read_delay=0, timeout=0,
            )

        def interpret_response(self, data):
            # when deriving from SensirionI2cCommand, check and remove CRCs now
            checked_data = SensirionI2cCommand.interpret_response(self, data)
            # return measure_interval_ms and delay_ms as a tuple(int, int)
            return unpack(">HH", checked_data)


Physical Value Conversion
^^^^^^^^^^^^^^^^^^^^^^^^^

If the value has a physical meaning but is transmitted with an offset and/or
scale factor, it's recommended to create a separate class to convert between
the underlying raw value and its physical value.

Example: Temperature transmitted as integers, with scale and offset.

.. sourcecode:: python

    from struct import pack, unpack

    class Sht3xTemperature():
        def __init__(self, ticks):
            self.ticks = ticks

        @property
        def degree_celsius(self):
            return (self.ticks / 100.0) - 70.0

        @staticmethod
        def from_degree_celsius(temperature):
            return Sht3xTemperature(round((temperature + 70.0) * 100.0))

        # Provide conversion to integer (used in the command class)
        def __int__(self):
            return self.ticks

        # Optional: Provide conversion to string, e.g. for printing
        def __str__(self):
            return "{:.2f} °C".format(self.degree_celsius)


    class Sht3xI2cCmdDataTypeExample(Sht3xI2cCmdBase):
        # Note: The passed parameters can either be simple integers (raw ticks)
        # or Sht3xTemperature objects since they provide a conversion to integer.
        def __init__(self, t_outside, t_inside):
            super(Sht3xI2cCmdDataTypeExample, self).__init__(
                tx_data=pack(">HH", int(t_outside), int(t_inside)),
                rx_length=4, read_delay=0, timeout=0,
            )

        def interpret_response(self, data):
            # when deriving from SensirionI2cCommand, check and remove CRCs now
            checked_data = SensirionI2cCommand.interpret_response(self, data)
            # return values as tuple(Sht3xTemperature, Sht3xTemperature)
            t_outside_ticks, t_inside_ticks = unpack(">HH", checked_data)
            return Sht3xTemperature(t_outside_ticks), Sht3xTemperature(t_inside_ticks)


These classes (``Sht3xTemperature`` in the example above) might be located in
a module named ``data_types.py`` within the driver package, and re-exported in
``__init__.py`` to make them easily importable by users.



Response Data Types
^^^^^^^^^^^^^^^^^^^

Sometimes a command returns a lot of different values. With the variants
mentioned above, this would lead
:py:meth:`~sensirion_i2c_driver.command.I2cCommand.interpret_response`
returning a tuple with many values, which is often cumbersome to use since the
values are only identified by their position in the tuple (i.e. are not named).

For such commands, you might consider creating a class to represent the whole
response data. There is no compulsory criteria when to use this variant or one
of the previously described variants. But as a rule of thumb, you may use this
variant if more than three values are returned.

.. sourcecode:: python

    from struct import unpack
    from .data_types import Sht3xTemperature

    class Sht3xExampleI2cResponse():
        def __init__(self, rx_data):
            self.rx_data = rx_data

        @property
        def measure_interval_ms(self):
            return unpack(">H", self.rx_data[0:2])[0]

        @property
        def temperature_outside(self):
            return Sht3xTemperature(self.rx_data[2:4])

        @property
        def temperature_inside(self):
            return Sht3xTemperature(self.rx_data[4:6])

        # Optional: Provide conversion to string, e.g. for printing
        def __str__(self):
            return "{:.2f} ms interval, {:.2f} °C outside, {:.2f} °C inside".format(
                self.measure_interval_ms, self.temperature_outside,
                self.temperature_inside)


    class Sht3xI2cCmdResponseTypeExample(Sht3xI2cCmdBase):
        def __init__(self):
            super(Sht3xI2cCmdResponseTypeExample, self).__init__(
                tx_data=None, rx_length=6, read_delay=0, timeout=0,
            )

        def interpret_response(self, data):
            # when deriving from SensirionI2cCommand, check and remove CRCs now
            checked_data = SensirionI2cCommand.interpret_response(self, data)
            # return values as a single Sht3xExampleI2cResponse object
            return Sht3xExampleI2cResponse(checked_data)


This even has the advantage that such response classes can easily be shared
between multiple command classes. For example if there are multiple different
"read measured values" commands which all return the same data structure,
you only have to implement the response data class once and every command
can use it to interpret its response.

These classes (``Sht3xExampleI2cResponse`` in the example above) might be
located in a module named ``data_types.py`` within the driver package, and
re-exported in ``__init__.py`` to make them easily importable by users.


Device Class
------------

The command classes mentioned above are fine to specify the I²C interface of
each command in an object oriented manner. This is useful for various special
use-cases, for example to execute I²C commands asynchronously on standalone I²C
masters, or for offline interpretation of logged raw I²C frames. In addition,
these command classes might be generated automatically by code generators if
a machine readable specification of the I²C commands is available.

But for the typical use-case of synchronously sending commands to a device and
waiting for the response, it's not very convenient to work with these command
classes directly. Therefore device drivers should provide a device class
(derived from :py:class:`~sensirion_i2c_driver.device.I2cDevice`) which is
basically a thin wrapper around the commands. Typically, each command is
wrapped by a corresponding method, with no additional logic added.

Example:

.. sourcecode:: python

    from sensirion_i2c_driver import I2cDevice
    from .commands import Sht3xI2cCmdSimpleExample, Sht3xI2cCmdDataTypeExample, \
        Sht3xI2cCmdResponseTypeExample


    class Sht3xI2cDevice(I2cDevice):

        def __init__(self, connection, slave_address=0x44):
            super(Sht3xI2cDevice, self).__init__(connection, slave_address)

        def simple_example(self, measure_interval_ms, delay_ms):
            return self.execute(Sht3xI2cCmdSimpleExample(measure_interval_ms, delay_ms))

        def data_type_example(self, t_outside, t_inside):
            return self.execute(Sht3xI2cCmdDataTypeExample(t_outside, t_inside))

        def response_type_example(self):
            return self.execute(Sht3xI2cCmdResponseExample())


.. note::

    Even if
    :py:meth:`~sensirion_i2c_driver.command.I2cCommand.interpret_response` of
    a command does not return any data, you must still return the result of
    :py:meth:`~sensirion_i2c_driver.device.I2cDevice.execute()`, because in
    multi channel mode this method will return a list containing the
    exception objects if I²C errors occurred.


.. warning::

    In some specific cases, it might still make sense to add some additional
    logic to these wrapper methods. Then you should keep in mind that
    :py:meth:`~sensirion_i2c_driver.device.I2cDevice.execute()` returns a list
    of values in case a multi channel transceiver is used. So you'll have to
    handle both, single channel return values and multi channel return values.
    Read the property
    :py:attr:`~sensirion_i2c_driver.connection.I2cConnection.is_multi_channel`
    of the underlying
    :py:class:`~sensirion_i2c_driver.connection.I2cConnection` to determine
    whether the returned value is a single- or multi channel response.

    In addition, for multi channel responses, keep in mind that the returned
    values might contain exception objects instead of received data. These need
    to be handled accordingly.

    Example:

    .. sourcecode:: python

        def simple_example(self, measure_interval_ms, delay_ms):
            result = self.execute(Sht3xI2cCmdSimpleExample(measure_interval_ms, delay_ms))

            # Multiply all received values by 2
            operation = lambda x: x if isinstance(x, Exception) else x * 2  # skip errors
            if self.connection.is_multi_channel:
                result = list(map(operation, result))  # convert result of each channel
            else:
                result = operation(result)  # convert the single channel result

            return result


API Example
-----------

From the user perspective, the API of such a device driver might look as
following:

.. sourcecode:: python

    from sensirion_i2c_sht.sht3x import Sht3xI2cDevice, Sht3xTemperature
    from sensirion_i2c_sht.sht3x.commands import Sht3xI2cCmdSimpleExample

    device = Sht3xI2cDevice(my_i2c_connection)

    # Simple example: Passed and returned data types are integers.
    measure_interval_ms, delay_ms = device.simple_example(1337, 42)
    print("Interval: {} ms, Delay: {} ms".format(measure_interval_ms, delay_ms))

    # Data type example: Passed data types are either integer or Sht3xTemperature
    # objects, returned data types are always Sht3xTemperature objects.
    t_outside, t_inside = device.data_type_example(42, Sht3xTemperature.from_degree_celsius(25.0))
    print("Temperature outside: {} °C".format(t_outside.degree_celsius))  # explicit
    print("Temperature inside: {}".format(t_inside))  # Using __str__() operator

    # Response type example: Returned data type is Sht3xExampleI2cResponse
    response = device.response_type_example()
    print("Interval: {} ms".format(response.measure_interval_ms))
    print("Temperature outside: {} °C".format(response.temperature_outside.degree_celsius))
    print("Temperature inside: {}".format(response.temperature_inside))

    # Direct use of command classes, e.g. to interpret offline data
    cmd = Sht3xI2cCmdSimpleExample()
    raw_received_data = b"\x00\x09\x09\x3A\x80\xA7"
    measure_interval_ms, delay_ms = cmd.interpret_response(raw_received_data)
