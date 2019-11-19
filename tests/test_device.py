# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_i2c_driver import I2cDevice, I2cConnection, I2cCommand
from mock import MagicMock


def test_single_channel_with_connection():
    transceiver = MagicMock()
    transceiver.API_VERSION = 1
    transceiver.channel_count = None
    transceiver.transceive.return_value = (0, None, b"\x11\x22")
    connection = I2cConnection(transceiver)
    device = I2cDevice(connection, 0x42)
    assert device.connection == connection
    assert device.slave_address == 0x42
    assert device.execute(I2cCommand(b"\x55", 3, 0.1, 0.2)) == b"\x11\x22"
    assert device.read() == b"\x11\x22"


def test_multi_channel():
    connection = MagicMock()
    connection.read.return_value = ["foo1", "foo2"]
    connection.execute.return_value = ["bar1", "bar2"]
    device = I2cDevice(connection, 0x42)
    assert device.execute(I2cCommand(b"\x55", 3, 0.1, 0.2)) == ["bar1", "bar2"]
    assert device.read() == ["foo1", "foo2"]


def test_single_channel_execute_asynchronous():
    connection = MagicMock()
    connection.read.return_value = ["foo1", "foo2"]
    device = I2cDevice(connection, 0x42)
    assert device.execute(I2cCommand(b"\x55", 3, 0.1, 0.2), True) is None
    assert device.read() == ["foo1", "foo2"]
