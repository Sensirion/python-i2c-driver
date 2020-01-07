# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_i2c_driver import SensirionWordI2cCommand, CrcCalculator
from sensirion_i2c_driver.errors import I2cChecksumError
import pytest


def test_empty():
    cmd = SensirionWordI2cCommand(None, None, None, 0.1, 0.2,
                                  CrcCalculator(8, 0x31, 0xFF))
    assert cmd.tx_data is None
    assert cmd.rx_length is None
    assert cmd.read_delay == 0.1
    assert cmd.timeout == 0.2


def test_only_command():
    cmd = SensirionWordI2cCommand(0x1337, None, None, 0.1, 0.2,
                                  CrcCalculator(8, 0x31, 0xFF))
    assert type(cmd.tx_data) is bytes
    assert cmd.tx_data == b"\x13\x37"
    assert cmd.rx_length is None
    assert cmd.read_delay == 0.1
    assert cmd.timeout == 0.2


def test_only_tx_data():
    cmd = SensirionWordI2cCommand(None, [0xDEAD, 0xBEEF], None, 0.1, 0.2,
                                  CrcCalculator(8, 0x31, 0xFF))
    assert type(cmd.tx_data) is bytes
    assert cmd.tx_data == b"\xDE\xAD\x98\xBE\xEF\x92"
    assert cmd.rx_length is None
    assert cmd.read_delay == 0.1
    assert cmd.timeout == 0.2


def test_command_and_tx_data():
    cmd = SensirionWordI2cCommand(0x1337, [0xDEAD, 0xBEEF], 5, 0.1, 0.2,
                                  CrcCalculator(8, 0x31, 0xFF))
    assert type(cmd.tx_data) is bytes
    assert cmd.tx_data == b"\x13\x37\xDE\xAD\x98\xBE\xEF\x92"
    assert cmd.rx_length is 5
    assert cmd.read_delay == 0.1
    assert cmd.timeout == 0.2


def test_interpret_response_empty():
    cmd = SensirionWordI2cCommand(None, None, 0, 0.1, 0.2,
                                  CrcCalculator(8, 0x31, 0xFF))
    response = cmd.interpret_response(b"")
    assert response is None


def test_interpret_response_2_bytes():
    cmd = SensirionWordI2cCommand(None, None, 2, 0.1, 0.2,
                                  CrcCalculator(8, 0x31, 0xFF))
    response = cmd.interpret_response(b"\xDE\xAD")
    assert type(response) is list
    assert response == [0xDEAD]


def test_interpret_response_6_bytes():
    cmd = SensirionWordI2cCommand(None, None, 6, 0.1, 0.2,
                                  CrcCalculator(8, 0x31, 0xFF))
    response = cmd.interpret_response(b"\xDE\xAD\x98\xBE\xEF\x92")
    assert type(response) is list
    assert response == [0xDEAD, 0xBEEF]


def test_interpret_response_crc_error():
    cmd = SensirionWordI2cCommand(None, None, 6, 0.1, 0.2,
                                  CrcCalculator(8, 0x31, 0xFF))
    with pytest.raises(I2cChecksumError):
        cmd.interpret_response(b"\xDE\xAD\x98\xBE\xEF\x93")  # wrong crc


def test_single_byte_command():
    cmd = SensirionWordI2cCommand(0x42, [0xDEAD, 0xBEEF], 5, 0.1, 0.2,
                                  CrcCalculator(8, 0x31, 0xFF), 1)
    assert type(cmd.tx_data) is bytes
    assert cmd.tx_data == b"\x42\xDE\xAD\x98\xBE\xEF\x92"
    assert cmd.rx_length is 5
    assert cmd.read_delay == 0.1
    assert cmd.timeout == 0.2
