# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_i2c_driver.errors import I2cError, I2cChecksumError, \
    I2cTransceiveError, I2cChannelDisabledError, I2cNackError, I2cTimeoutError


def test_i2c_error():
    error = I2cError(b"\x55", "Error")
    assert error.received_data == b"\x55"
    assert error.error_message == "Error"
    assert str(error) == "Error"


def test_i2c_checksum_error():
    error = I2cChecksumError(0x11, 0x22, b"\x55")
    assert error.received_checksum == 0x11
    assert error.expected_checksum == 0x22
    assert error.received_data == b"\x55"
    expected_msg = "I2C error: Received wrong checksum 0x11 (expected 0x22)."
    assert error.error_message == expected_msg
    assert str(error) == expected_msg


def test_i2c_transceive_error():
    error = I2cTransceiveError("some error", b"\x55", "Hello world")
    assert error.transceiver_error == "some error"
    assert error.received_data == b"\x55"
    expected_msg = "I2C transceive failed: Hello world"
    assert error.error_message == expected_msg
    assert str(error) == expected_msg


def test_i2c_channel_disabled_error():
    transceiver_error = Exception(42)
    error = I2cChannelDisabledError(transceiver_error, b"\x55")
    assert error.transceiver_error == transceiver_error
    assert error.received_data == b"\x55"
    expected_msg = "I2C transceive failed: Channel is disabled (42)."
    assert error.error_message == expected_msg
    assert str(error) == expected_msg


def test_i2c_nack_error():
    transceiver_error = Exception(42)
    error = I2cNackError(transceiver_error, b"\x55")
    assert error.transceiver_error == transceiver_error
    assert error.received_data == b"\x55"
    expected_msg = "I2C transceive failed: NACK (byte not acknowledged)."
    assert error.error_message == expected_msg
    assert str(error) == expected_msg


def test_i2c_timeout_error():
    transceiver_error = Exception(42)
    error = I2cTimeoutError(transceiver_error, b"\x55")
    assert error.transceiver_error == transceiver_error
    assert error.received_data == b"\x55"
    expected_msg = "I2C transceive failed: Timeout."
    assert error.error_message == expected_msg
    assert str(error) == expected_msg
