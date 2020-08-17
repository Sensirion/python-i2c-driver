.. _single_multi_channel_mode:

Single/Multi-Channel Mode
=========================

This driver (particularly
:py:class:`~sensirion_i2c_driver.connection.I2cConnection` and
:py:class:`~sensirion_i2c_driver.device.I2cDevice`) supports two different
modes of operation: single channel and multi channel.


.. _single_channel_mode:

Single Channel
--------------

This mode allows to communicate with a single I²C bus at a time, which is the
typical use-case. In this mode, the method
:py:meth:`~sensirion_i2c_driver.connection.I2cConnection.execute` of
:py:class:`~sensirion_i2c_driver.connection.I2cConnection` returns directly the
interpreted response (e.g. a `float`) of the executed command if the operation
was successful, or raise an exception in case of an error (NACK, timeout, ...).

**Example:**

.. sourcecode:: python

    device = MyI2cDevice(I2cConnection(some_single_channel_transceiver))
    result = device.get_serial_number()  # command returning a string

    # result contains e.g. "BEEF"


.. _multi_channel_mode:

Multi Channel
-------------

In this mode, communication is done concurrently on multiple I²C buses. At
Sensirion this is often used to execute measurements on multiple sensors at
the same time. In this mode, the method
:py:meth:`~sensirion_i2c_driver.connection.I2cConnection.execute` of
:py:class:`~sensirion_i2c_driver.connection.I2cConnection` returns a list
containing the results for each channel. Each result is either the interpreted
response of the executed command (if successful), or an exception object (in
case of an error).

**In contrast to the single channel mode, no exception is raised in case of
I²C errors!** This way you still get the results from successful channels if
errors occurred on some of the channels, but you'll have to check the results
by yourself. Especially for commands which do not return any data, you still
have to check the returned results to ensure the commands were executed
successfully.

.. note:: Even though the mentioned methods will not raise an exception in
          case of I²C errors, they may still raise an exception if for some
          reason the commands could not be executed at all, for example if the
          I²C transceiver got disconnected from the computer.


**Example:**

.. sourcecode:: python

    device = MyI2cDevice(I2cConnection(some_multi_channel_transceiver))
    result = device.get_serial_number()  # command returning a string

    # result contains e.g. ["DEAD", "BEEF", I2cTimeoutError()]
    #  -> read serial number from I²C bus 0: "DEAD"
    #  -> read serial number from I²C bus 1: "BEEF"
    #  -> read serial number from I²C bus 2 failed with timeout error


Choose Mode
-----------

Which mode is used depends on the underlying
:ref:`I²C transceiver<transceivers>`. A multi channel transceiver will activate
the multi channel mode, and a single channel transceiver will activate the
single channel mode.

But in some cases it might be easier to always have the same API, independent
of whether a multi- or single channel transceiver is used. Then you can
enforce to always use multi channel responses with the property
:py:attr:`~sensirion_i2c_driver.connection.I2cConnection.always_multi_channel_response`
of :py:class:`~sensirion_i2c_driver.connection.I2cConnection`. For single
channel transceivers, the result will then always be a list containing one
item. The behavior of multi channel transceivers is not affected by this
property.

**Example:**

.. sourcecode:: python

    connection = I2cConnection(some_single_channel_transceiver)
    connection.always_multi_channel_response = True  # <-- here
    device = MyI2cDevice(connection)
    result = device.get_serial_number()  # command returning a string

    # result contains e.g. ['BEEF']
