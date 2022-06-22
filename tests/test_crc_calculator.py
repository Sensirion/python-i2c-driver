# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_i2c_driver import CrcCalculator
import pytest


@pytest.mark.parametrize("calculator,input_data,expected_crc", [
    # CRC-8/SENSIRION
    (CrcCalculator(8, 0x31, 0xFF), [], 0xFF),
    (CrcCalculator(8, 0x31, 0xFF), [0xBE, 0xEF], 0x92),
    (CrcCalculator(8, 0x31, 0xFF), bytearray([0xBE, 0xEF]), 0x92),
    # CRC-16/GENIBUS
    (CrcCalculator(16, 0x1021, 0xFFFF, 0xFFFF), [], 0x0000),
    (CrcCalculator(16, 0x1021, 0xFFFF, 0xFFFF), [0xDEAD, 0xBEEF], 0xBF68),
    # CRC-32/POSIX
    (CrcCalculator(32, 0x04C11DB7, 0x0, 0xFFFFFFFF), [], 0xFFFFFFFF),
    (CrcCalculator(32, 0x04C11DB7, 0x0, 0xFFFFFFFF), [0xDEADBEEF, 0xC0EDBABE],
        0xF197A443),
])
def test_8bit_0x31_0xFF(calculator, input_data, expected_crc):
    # check two times with same calculator to see if it is stateless
    assert calculator(input_data) == expected_crc
    assert calculator(input_data) == expected_crc
