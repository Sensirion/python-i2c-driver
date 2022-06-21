# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_i2c_driver import LinuxI2cTransceiver


def test_open_close_file(tmpdir):
    device_file = tmpdir.join("device")
    device_file.ensure()
    with LinuxI2cTransceiver(str(device_file)) as transceiver:
        assert transceiver.description == str(device_file)
        assert transceiver.channel_count is None
