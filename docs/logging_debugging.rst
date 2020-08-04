Logging / Debugging
===================

Every module of this package uses the `Python Logging Facility`_ to log debug
messages, warnings etc. This page gives a quick overview how it works.

Usage
-----

To enable the logging facility in your project, just add the following lines
to the top of your main Python script:

.. sourcecode:: python

    import logging
    logging.basicConfig()


Log Raw Transmitted/Received Data
---------------------------------

When debugging issues on a lower layer, it might be useful to see what data
(raw bytes) is actually sent to the underlying transceiver, and what data is
received from the connected devices. This data can be shown by changing the
logging level to ``DEBUG``:

.. sourcecode:: python

    from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection, \
        I2cDevice, I2cCommand

    import logging
    logging.basicConfig(level=logging.DEBUG)  # <- logging level set here

    with LinuxI2cTransceiver('/dev/i2c-1') as transceiver:
        device = I2cDevice(I2cConnection(transceiver), slave_address=0x69)
        response = device.execute(I2cCommand(tx_data=b"\x80\x04", rx_length=6,
                                             read_delay=5e-3, timeout=0))
        print("Received {} bytes".format(len(response)))


This way the raw data is printed to the console:

.. sourcecode:: console

    DEBUG:sensirion_i2c_driver.connection:I2cConnection send raw: slave_address=105 rx_length=6 read_delay=0.005 timeout=0.0 tx_data=[0x80, 0x04]
    DEBUG:sensirion_i2c_driver.connection:I2cConnection received raw: [0x00, 0x09, 0x09, 0x3A, 0x80, 0xA7]
    Received 6 bytes


Change Logging Verbosity of Modules
-----------------------------------

Since every module contains its own logging object ``log``, it's even possible
to set the logging level of each module independently. For example, the
verbosity of the :py:class:`~sensirion_i2c_driver.connection.I2cConnection`
class could be reduced by changing its logging level to ``CRITICAL`` (i.e.
only critical messages will be logged):

.. sourcecode:: python

    import sensirion_i2c_driver
    from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection, \
        I2cDevice, I2cCommand

    import logging
    logging.basicConfig(level=logging.DEBUG)

    # Make connection less verbose
    sensirion_i2c_driver.connection.log.setLevel(level=logging.CRITICAL)

    with LinuxI2cTransceiver('/dev/i2c-1') as transceiver:
        device = I2cDevice(I2cConnection(transceiver), slave_address=0x69)
        response = device.execute(I2cCommand(tx_data=b"\x80\x04", rx_length=6,
                                             read_delay=5e-3, timeout=0))
        print("Received {} bytes".format(len(response)))


This way you won't see the raw transmitted data:

.. sourcecode:: console

    Received 6 bytes


.. _Python Logging Facility: https://docs.python.org/3/library/logging.html
