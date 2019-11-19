# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_i2c_driver import I2cConnection, I2cCommand
from sensirion_i2c_driver.errors import I2cNackError, I2cTimeoutError
from mock import MagicMock
import pytest


def test_v1_single_channel_write():
    transceiver = MagicMock()
    transceiver.API_VERSION = 1
    transceiver.channel_count = None
    transceiver.transceive.return_value = (0, None, b"")
    connection = I2cConnection(transceiver)
    response = connection.write(0x42, I2cCommand(b"\x55", 3, 0.1, 0.2))
    args = [kwargs for args, kwargs in transceiver.transceive.call_args_list]
    assert args == [
        {
            "slave_address": 0x42,
            "tx_data": b"\x55",
            "rx_length": None,  # no read!
            "read_delay": 0.0,  # no read!
            "timeout": 0.2,
        },
    ]
    assert response is None


def test_v1_single_channel_read():
    transceiver = MagicMock()
    transceiver.API_VERSION = 1
    transceiver.channel_count = None
    transceiver.transceive.return_value = (0, None, b"\x11\x22\x33")
    connection = I2cConnection(transceiver)
    response = connection.read(0x42, I2cCommand(b"\x55", 3, 0.1, 0.2))
    args = [kwargs for args, kwargs in transceiver.transceive.call_args_list]
    assert args == [
        {
            "slave_address": 0x42,
            "tx_data": None,  # no write!
            "rx_length": 3,
            "read_delay": 0.0,  # no write!
            "timeout": 0.2,
        },
    ]
    assert response == b"\x11\x22\x33"


def test_v1_single_channel_execute():
    transceiver = MagicMock()
    transceiver.API_VERSION = 1
    transceiver.channel_count = None
    transceiver.transceive.return_value = (0, None, b"\x11\x22\x33")
    connection = I2cConnection(transceiver)
    response = connection.execute(0x42, I2cCommand(b"\x55", 3, 0.1, 0.2))
    args = [kwargs for args, kwargs in transceiver.transceive.call_args_list]
    assert args == [
        {
            "slave_address": 0x42,
            "tx_data": b"\x55",
            "rx_length": 3,
            "read_delay": 0.1,
            "timeout": 0.2,
        },
    ]
    assert response == b"\x11\x22\x33"


def test_v1_single_channel_error():
    transceiver = MagicMock()
    transceiver.API_VERSION = 1
    transceiver.channel_count = None
    transceiver.transceive.return_value = (3, Exception("timeout"), b"")
    connection = I2cConnection(transceiver)
    with pytest.raises(I2cTimeoutError):
        connection.execute(0x42, I2cCommand(b"\x55", 3, 0.1, 0.2))


def test_v1_single_channel_execute_always_multi_channel_response():
    transceiver = MagicMock()
    transceiver.API_VERSION = 1
    transceiver.channel_count = None
    transceiver.transceive.return_value = (0, None, b"\x11\x22\x33")
    connection = I2cConnection(transceiver)
    connection.always_multi_channel_response = True
    response = connection.execute(0x42, I2cCommand(b"\x55", 3, 0.1, 0.2))
    args = [kwargs for args, kwargs in transceiver.transceive.call_args_list]
    assert args == [
        {
            "slave_address": 0x42,
            "tx_data": b"\x55",
            "rx_length": 3,
            "read_delay": 0.1,
            "timeout": 0.2,
        },
    ]
    assert response == [b"\x11\x22\x33"]


def test_v1_multi_channel_execute():
    transceiver = MagicMock()
    transceiver.API_VERSION = 1
    transceiver.channel_count = 2
    transceiver.transceive.return_value = [
        (0, None, b"\x11\x22\x33"),
        (2, Exception("NACK"), b""),
    ]
    connection = I2cConnection(transceiver)
    response = connection.execute(0x42, I2cCommand(b"\x55", 3, 0.1, 0.2))
    args = [kwargs for args, kwargs in transceiver.transceive.call_args_list]
    assert args == [
        {
            "slave_address": 0x42,
            "tx_data": b"\x55",
            "rx_length": 3,
            "read_delay": 0.1,
            "timeout": 0.2,
        },
    ]
    assert len(response) == 2
    assert response[0] == b"\x11\x22\x33"
    assert type(response[1]) is I2cNackError
