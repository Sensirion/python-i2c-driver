# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_i2c_driver import I2cConnection, I2cCommand
from sensirion_i2c_driver.errors import I2cNackError, I2cTimeoutError
from mock import MagicMock
import pytest


def test_always_multi_channel_response_default_false():
    transceiver = MagicMock()
    connection = I2cConnection(transceiver)
    assert connection.always_multi_channel_response is False


def test_always_multi_channel_response_get_set():
    transceiver = MagicMock()
    connection = I2cConnection(transceiver)
    connection.always_multi_channel_response = True
    assert connection.always_multi_channel_response is True


def test_v1_single_channel_is_multi_channel():
    transceiver = MagicMock()
    transceiver.API_VERSION = 1
    transceiver.channel_count = None  # single channel
    connection = I2cConnection(transceiver)
    assert connection.is_multi_channel is False


def test_v1_multi_channel_is_multi_channel():
    transceiver = MagicMock()
    transceiver.API_VERSION = 1
    transceiver.channel_count = 1  # multi channel
    connection = I2cConnection(transceiver)
    assert connection.is_multi_channel is True


def test_v1_single_channel_but_always_multi_is_multi_channel():
    transceiver = MagicMock()
    transceiver.API_VERSION = 1
    transceiver.channel_count = None  # single channel
    connection = I2cConnection(transceiver)
    connection.always_multi_channel_response = True
    assert connection.is_multi_channel is True


def test_v1_multi_channel_and_always_multi_is_multi_channel():
    transceiver = MagicMock()
    transceiver.API_VERSION = 1
    transceiver.channel_count = 3  # multi channel
    connection = I2cConnection(transceiver)
    connection.always_multi_channel_response = True
    assert connection.is_multi_channel is True


def test_is_multi_channel_with_unsupported_api_version():
    transceiver = MagicMock()
    transceiver.API_VERSION = 99  # unsupported
    connection = I2cConnection(transceiver)
    with pytest.raises(Exception, match=r".*not supported.*"):
        connection.is_multi_channel


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


def test_v1_single_channel_execute_wait_post_process_true():
    transceiver = MagicMock()
    transceiver.API_VERSION = 1
    transceiver.channel_count = None
    transceiver.transceive.return_value = (0, None, b"\x11\x22\x33")
    connection = I2cConnection(transceiver)
    response = connection.execute(0x42, I2cCommand(b"\x55", 3, 0.1, 0.2, 0.1),
                                  wait_post_process=True)
    assert response == b"\x11\x22\x33"


def test_v1_single_channel_execute_wait_post_process_false():
    transceiver = MagicMock()
    transceiver.API_VERSION = 1
    transceiver.channel_count = None
    transceiver.transceive.return_value = (0, None, b"\x11\x22\x33")
    connection = I2cConnection(transceiver)
    response = connection.execute(0x42, I2cCommand(b"\x55", 3, 0.1, 0.2, 0.1),
                                  wait_post_process=False)
    assert response == b"\x11\x22\x33"
