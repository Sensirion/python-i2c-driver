# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from .errors import I2cTransceiveError, I2cChannelDisabledError, \
    I2cNackError, I2cTimeoutError
from .transceiver_v1 import I2cTransceiverV1

import logging
log = logging.getLogger(__name__)


class I2cConnection(object):
    """
    I²C connection class to allow executing I²C commands with a higher-level,
    transceiver-independent API.

    The connection supports two different modes of operation: Single channel
    and multi channel. See :ref:`single_multi_channel_mode` for details.
    """

    def __init__(self, transceiver):
        """
        Creates an I²C connection object.

        :param transceiver:
            An I²C transceiver object of any API version (type depends on the
            used hardware).
        """
        super(I2cConnection, self).__init__()
        self._transceiver = transceiver
        self._always_multi_channel_response = False

    @property
    def always_multi_channel_response(self):
        """
        Set this to True to enforce the behaviour of a multi-channel
        connection, even if a single-channel transceiver is used. In
        particular, it makes the method
        :py:meth:`~sensirion_i2c_driver.connection.I2cConnection.execute`
        always returning a list, without throwing an exception in case of
        communication errors. This might be useful for applications where
        both, single-channel and multi-channel communication is needed.

        :type: Bool
        """
        return self._always_multi_channel_response

    @always_multi_channel_response.setter
    def always_multi_channel_response(self, value):
        self._always_multi_channel_response = value

    def execute(self, slave_address, command):
        """
        Perform write and read operations of an I²C command.

        :param byte slave_address:
            The slave address of the device to communicate with.
        :param ~sensirion_i2c_driver.command.I2cCommand command:
            The command to execute.
        :return:
            - In single channel mode: The interpreted data of the command.
            - In multi-channel mode: A list containing either interpreted data
              of the command (on success) or an Exception object (on error)
              for every channel.
        :raise:
            In single-channel mode, an exception is raised in case of
            communication errors.
        """
        return self._interpret_response(command, self._transceive(
            slave_address=slave_address,
            tx_data=command.tx_data,
            rx_length=command.rx_length,
            read_delay=command.read_delay,
            timeout=command.timeout,
        ))

    def _transceive(self, slave_address, tx_data, rx_length, read_delay,
                    timeout):
        """
        API version independent wrapper around the transceiver.
        """
        api_methods_dict = {
            1: self._transceive_v1,
        }
        if self._transceiver.API_VERSION in api_methods_dict:
            return api_methods_dict[self._transceiver.API_VERSION](
                slave_address, tx_data, rx_length, read_delay, timeout)
        else:
            raise Exception("The I2C transceiver API version {} is not "
                            "supported. You might need to update the "
                            "sensirion-i2c-driver package.".format(
                                self._transceiver.API_VERSION))

    def _transceive_v1(self, slave_address, tx_data, rx_length, read_delay,
                       timeout):
        """
        Helper function to transceive a command with a API V1 transceiver.
        """
        result = self._transceiver.transceive(
            slave_address=slave_address,
            tx_data=tx_data,
            rx_length=rx_length,
            read_delay=read_delay,
            timeout=timeout,
        )
        if self._transceiver.channel_count is not None:
            return [self._convert_result_v1(r) for r in result]
        else:
            return self._convert_result_v1(result)

    def _convert_result_v1(self, result):
        """
        Helper function to convert the returned data from a API V1 transceiver.
        """
        status, error, rx_data = result
        if status == I2cTransceiverV1.STATUS_OK:
            return rx_data
        elif status == I2cTransceiverV1.STATUS_CHANNEL_DISABLED:
            return I2cChannelDisabledError(error, rx_data)
        elif status == I2cTransceiverV1.STATUS_NACK:
            return I2cNackError(error, rx_data)
        elif status == I2cTransceiverV1.STATUS_TIMEOUT:
            return I2cTimeoutError(error, rx_data)
        else:
            return I2cTransceiveError(error, rx_data, str(error))

    def _interpret_response(self, command, response):
        """
        Helper function to interpret the returned data from the transceiver.
        """
        if isinstance(response, list):
            # It's a multi channel transceiver -> interpret response of each
            # channel separately and return them as a list. Don't raise
            # exceptions to avoid loosing other channels data if one channel
            # has an issue.
            return [self._interpret_single_response(command, ch)
                    for ch in response]
        elif self._always_multi_channel_response is True:
            # Interpret the response of a single channel, but return it like a
            # multi channel response as a list and without raising exceptions.
            return [self._interpret_single_response(command, response)]
        else:
            # Interpret the response of a single channel and raise the
            # exception if there is one.
            response = self._interpret_single_response(command, response)
            if isinstance(response, Exception):
                raise response
            else:
                return response

    def _interpret_single_response(self, command, response):
        """
        Helper function to interpret the returned data of a single channel
        from the transceiver. Returns either the interpreted response, or
        an exception.
        """
        try:
            if isinstance(response, Exception):
                return response
            else:
                return command.interpret_response(response)
        except Exception as e:
            return e
