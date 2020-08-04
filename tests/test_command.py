# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_i2c_driver import I2cCommand


def test_tx_data_none():
    cmd = I2cCommand(None, 42, 0.1, 0.2, 0.0)
    assert cmd.tx_data is None


def test_tx_data_empty_bytes():
    cmd = I2cCommand(b"", 42, 0.1, 0.2, 0.0)
    assert type(cmd.tx_data) is bytes
    assert cmd.tx_data == b""


def test_tx_data_bytes():
    cmd = I2cCommand(b"\x11\x22", 42, 0.1, 0.2, 0.0)
    assert type(cmd.tx_data) is bytes
    assert cmd.tx_data == b"\x11\x22"


def test_tx_data_bytearray():
    cmd = I2cCommand(bytearray([0x11, 0x22]), 42, 0.1, 0.2, 0.0)
    assert type(cmd.tx_data) is bytes
    assert cmd.tx_data == b"\x11\x22"


def test_tx_data_list():
    cmd = I2cCommand([0x11, 0x22], 42, 0.1, 0.2, 0.0)
    assert type(cmd.tx_data) is bytes
    assert cmd.tx_data == b"\x11\x22"


def test_rx_length_none():
    cmd = I2cCommand(b"\x11", None, 0.1, 0.2, 0.0)
    assert cmd.rx_length is None


def test_rx_length_zero():
    cmd = I2cCommand(b"\x11", 0, 0.1, 0.2, 0.0)
    assert type(cmd.rx_length) is int
    assert cmd.rx_length == 0


def test_rx_length_int():
    cmd = I2cCommand(b"\x11", 42, 0.1, 0.2, 0.0)
    assert type(cmd.rx_length) is int
    assert cmd.rx_length == 42


def test_read_delay_int():
    cmd = I2cCommand(b"\x11", 42, 1, 0.2, 0.0)
    assert type(cmd.read_delay) is float
    assert cmd.read_delay == 1.0


def test_read_delay_float():
    cmd = I2cCommand(b"\x11", 42, 0.1, 0.2, 0.0)
    assert type(cmd.read_delay) is float
    assert cmd.read_delay == 0.1


def test_timeout_int():
    cmd = I2cCommand(b"\x11", 42, 1, 2, 0.0)
    assert type(cmd.timeout) is float
    assert cmd.timeout == 2.0


def test_timeout_float():
    cmd = I2cCommand(b"\x11", 42, 0.1, 0.2, 0.0)
    assert type(cmd.timeout) is float
    assert cmd.timeout == 0.2


def test_post_processing_time_defaults_to_zero():
    cmd = I2cCommand(b"\x11", 42, 1, 2)  # post processing time not passed
    assert type(cmd.post_processing_time) is float
    assert cmd.post_processing_time == 0.0


def test_post_processing_time_int():
    cmd = I2cCommand(b"\x11", 42, 1, 2, 5)
    assert type(cmd.post_processing_time) is float
    assert cmd.post_processing_time == 5.0


def test_post_processing_time_float():
    cmd = I2cCommand(b"\x11", 42, 0.1, 0.2, 2.3)
    assert type(cmd.post_processing_time) is float
    assert cmd.post_processing_time == 2.3


def test_interpret_response_empty():
    cmd = I2cCommand(b"\x11", 42, 0.1, 0.2, 0.0)
    response = cmd.interpret_response(b"")
    assert response is None


def test_interpret_response_bytes():
    cmd = I2cCommand(b"\x11", 42, 0.1, 0.2, 0.0)
    response = cmd.interpret_response(b"\x55\x66")
    assert type(response) is bytes
    assert response == b"\x55\x66"
