Quick Start
===========

Following example code shows how the driver is intended to use:

.. sourcecode:: python

    from struct import pack
    from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection, \
        I2cDevice, SensirionWordI2cCommand, CrcCalculator


    # Implement a command
    class MyI2cCmdReadSerialNumber(SensirionWordI2cCommand):
        def __init__(self):
            super(MyI2cCmdReadSerialNumber, self).__init__(
                command=0xD033,
                tx_words=[],
                rx_length=48,
                read_delay=0,
                timeout=0,
                crc=CrcCalculator(8, 0x31, 0xFF),
            )

        def interpret_response(self, data):
            words = SensirionWordI2cCommand.interpret_response(self, data)
            sn_bytes = pack('>16H', *words)
            return str(sn_bytes.decode('utf-8').rstrip('\0'))


    # Implement a device
    class MyI2cDevice(I2cDevice):
        def __init__(self, connection, slave_address=0x69):
            super(MyI2cDevice, self).__init__(connection, slave_address)

        def read_serial_number(self):
            return self.execute(MyI2cCmdReadSerialNumber())


    # Usage
    with LinuxI2cTransceiver('/dev/i2c-1') as transceiver:
        device = MyI2cDevice(I2cConnection(transceiver))
        print("Serial Number: {}".format(device.get_serial_number()))
