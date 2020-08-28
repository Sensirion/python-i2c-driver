Error Handling
==============

This page gives you an overview how and which errors are handled by the driver,
and how the user has to implement error handling. Since it is heavily related
to the :ref:`single_multi_channel_mode`, you should read that documentation
first.

The following errors can occur when executing I²C commands:

- Slave didn't acknowledge the data from the master (NACK): In this case,
  you'll get an :py:class:`~sensirion_i2c_driver.errors.I2cTransceiveError`,
  or its derived (i.e. more specific) error
  :py:class:`~sensirion_i2c_driver.errors.I2cNackError`. It depends on the
  capabilities of the underlying I²C transceiver which error you'll get.
- Slave stretched the clock line longer than expected (clock stretching
  timeout): Similar to the NACK error, you'll get an
  :py:class:`~sensirion_i2c_driver.errors.I2cTransceiveError`,
  or its derived error :py:class:`~sensirion_i2c_driver.errors.I2cTimeoutError`.
- On multi channel I²C transceivers, it's possible that some specific I²C
  channels are simply disabled, i.e. no I²C commands will be executed on these
  channels. Such channels will return the error
  :py:class:`~sensirion_i2c_driver.errors.I2cChannelDisabledError`.
- If the response of the executed I²C command contains CRCs (like
  :py:class:`~sensirion_i2c_driver.sensirion_command.SensirionI2cCommand`),
  you'll get an :py:class:`~sensirion_i2c_driver.errors.I2cChecksumError` if
  at least one received CRC was wrong.
- The :py:meth:`~sensirion_i2c_driver.command.I2cCommand.interpret_response`
  method of executed commands might even raise any other exception which is
  then forwarded to you like any other error described above.
- If the execution of I²C commands by the underlying transceiver completely
  failes, the transceiver might raise a transceiver specific exception which
  will not be handled by this driver at all. So it will propagate directly up
  into the user code.


Single Channel Error Handling
-----------------------------

In :ref:`single_channel_mode` mode, you can handle errors just the usual way
with ``try``/``except``:

.. sourcecode:: python

    from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection, \
        I2cDevice, I2cCommand
    from sensirion_i2c_driver.errors import I2cNackError, I2cChecksumError


    class MyI2cDevice(I2cDevice):
        def __init__(self, connection):
            super(MyI2cDevice, self).__init__(connection, slave_address=0x69)

        def do_something(self):
            return self.execute(I2cCommand(tx_data=b"\x80\x04", rx_length=6,
                                           read_delay=5e-3, timeout=0))


    with LinuxI2cTransceiver('/dev/i2c-1') as transceiver:
        connection = I2cConnection(transceiver)
        device = MyI2cDevice(connection)

        # Handle any error the same way
        try:
            response = device.do_something()
            print("Response: {}".format(response))
        except Exception as e:
            print("Error: {}".format(str(e)))

        # Handle NACK and CRC errors separately
        try:
            response = device.do_something()
            print("Response: {}".format(response))
        except I2cNackError as e:
            print("Error: Slave did not acknowledge!")
        except I2cChecksumError as e:
            print("Error: Received wrong CRC!")
        except Exception as e:
            print("Error: {}".format(str(e)))


Multi Channel Error Handling
----------------------------

In :ref:`multi_channel_mode` mode, error handling is slighly more complicated
since exceptions are not raised, but returned as items within the list of
responses.

.. sourcecode:: python

    from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection, \
        I2cDevice, I2cCommand
    from sensirion_i2c_driver.errors import I2cNackError, I2cChecksumError


    class MyI2cDevice(I2cDevice):
        def __init__(self, connection):
            super(MyI2cDevice, self).__init__(connection, slave_address=0x69)

        def do_something(self):
            return self.execute(I2cCommand(tx_data=b"\x80\x04", rx_length=6,
                                           read_delay=5e-3, timeout=0))


    with LinuxI2cTransceiver('/dev/i2c-1') as transceiver:
        connection = I2cConnection(transceiver)
        connection.always_multi_channel_response = True  # Make it multi channel
        device = MyI2cDevice(connection)

        # do_something() will always return a list, even if I²C errors occurred
        responses = device.do_something()

        # Just check if none of the responses is an error
        if any(isinstance(response, Exception) for response in responses):
            print("The command failed on at least one channel!")

        # Print all responses
        for response in responses:
            if isinstance(response, Exception):
                print("Error: {}".format(str(response)))
            else:
                print("Response: {}".format(str(response)))

        # Convert all response values (example: multiply by 2), except errors
        responses = map(lambda x: x if isinstance(x, Exception) else x * 2, responses)
