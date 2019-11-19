# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function


class I2cDevice(object):
    """
    Base class for all I²C devices. Users should inherit from this class when
    implementing new I²C device drivers since it provides following convenience
    methods:

    - :py:meth:`~sensirion_i2c_driver.device.I2cDevice.execute` allows to
      execute :py:class:`~sensirion_i2c_driver.command.I2cCommand` objects and
      returns the interpreted response.
    - :py:meth:`~sensirion_i2c_driver.device.I2cDevice.read` allows to
      perform only the I²C read operation (without preceding write operation)
      and returns the interpreted response by using the last sent
      :py:class:`~sensirion_i2c_driver.command.I2cCommand`.
    """
    def __init__(self, connection, slave_address):
        """
        Create an I²C device instance on a given connection.

        :param ~sensirion_i2c_driver.connection.I2cConnection connection:
            The I²C connection used to execute the commands.
        :param byte slave_address:
            The I²C slave address of the device.
        """
        super(I2cDevice, self).__init__()
        self._connection = connection
        self._slave_address = slave_address
        self._last_command = None

    @property
    def connection(self):
        """
        Get the used I²C connection.

        :return: The used I²C connection.
        :rtype: ~sensirion_i2c_driver.connection.I2cConnection
        """
        return self._connection

    @property
    def slave_address(self):
        """
        Get the I²C slave address.

        :return: The I²C slave address.
        :rtype: byte
        """
        return self._slave_address

    def execute(self, command, asynchronous=False):
        """
        Execute an I²C command on this device.

        :param ~sensirion_i2c_driver.command.I2cCommand command:
            The command to be executed.
        :param Bool asynchronous:
            If ``True``, only the write operation will be performed and no
            result is returned. If ``False``, the read operation will be
            performed too and the received response is returned. Defaults to
            ``False``.
        :return:
            The interpreted response will be returned, or ``None`` if
            ``asynchronous`` is ``True``.
        :rtype:
            Depends on the executed command.
        """
        self._last_command = command
        if asynchronous:
            self._connection.write(self._slave_address, command)
        else:
            return self._connection.execute(self._slave_address, command)

    def read(self):
        """
        Perform an I²C read operation on this device, using the last sent
        command to interpret its response.

        :return:
            The interpreted response.
        :rtype:
            Depends on the executed command.
        """
        return self._connection.read(self._slave_address, self._last_command)
