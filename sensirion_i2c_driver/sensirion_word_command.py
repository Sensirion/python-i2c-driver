# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from .command import I2cCommand
from .errors import I2cChecksumError
from struct import pack


class SensirionWordI2cCommand(I2cCommand):
    """
    Base class for Sensirion-specific I²C commands as used in most Sensirion
    sensor devices. This class extends the base class
    :py:class:`~sensirion_i2c_driver.command.I2cCommand` with a word (2 byte)
    oriented interface and allows transparent insertion resp. verification of
    CRC bytes following each word.
    """

    def __init__(self, command, tx_words, rx_length, read_delay, timeout, crc,
                 command_bytes=2):
        """
        Constructs a new Sensirion word-oriented I²C command.

        :param int/None command:
            The command word to be sent to the device. None means that no
            command will be sent, i.e. only ``tx_words`` (if not None) will
            be sent.
        :param list/None tx_words:
            Words (list of integers) to be sent to the I²C device. None means
            that no write header will be sent at all (if ``command`` is None
            too). An empty list means to send the write header (even if
            ``command`` is None), but without data following it.
        :param int/None rx_length:
            Number of bytes to be read from the I²C device, inclusing CRC
            bytes. None means that no read header is sent at all. Zero means
            to send the read header, but without reading any data.
        :param float read_delay:
            Delay (in Seconds) to be inserted between the end of the write
            operation and the beginning of the read operation. This is needed
            if the device needs some time to prepare the RX data, e.g. if it
            has to perform a measurement. Set to 0.0 to indicate that no delay
            is needed, i.e. the device does not need any processing time.
        :param float timeout:
            Timeout (in Seconds) to be used in case of clock stretching. If the
            device stretches the clock longer than this value, the transceive
            operation will be aborted with a timeout error. Set to 0.0 to
            indicate that the device will not stretch the clock for this
            command.
        :param calleable crc:
            A :py:class:`~sensirion_i2c_driver.crc_calculator.CrcCalculator`
            object to calculate the CRC of the transceived data, or any other
            calleable object or function which takes a bytearray as parameter
            and returns its CRC as an integer. If the command does not contain
            CRC bytes, pass None to disable it.
        :param int command_bytes:
            Number of command bytes. Most Sensirion sensors use a 2-byte
            command (thus it is the default), but there are also sensors using
            only one byte for the command.
        """
        super(SensirionWordI2cCommand, self).__init__(
            tx_data=self._build_tx_data(command, command_bytes, tx_words, crc),
            rx_length=rx_length,
            read_delay=read_delay,
            timeout=timeout,
        )
        self._crc = crc

    def interpret_response(self, data):
        """
        Converts the raw response from the device to words (2 bytes), checks
        their CRC and retunrs the checked words.

        :param bytes data:
            Received raw bytes from the read operation.
        :return:
            The received words, or None if there is no data received.
        :rtype:
            list(int) or None
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        data = bytearray(data)  # Python 2 compatibility
        words = []
        bytes_per_word = 3 if self._crc is not None else 2
        for i in range(len(data)):
            if i % bytes_per_word == 0:
                next_word = data[i] << 8
            elif i % bytes_per_word == 1:
                next_word += data[i]
                words.append(next_word)
            else:
                received_crc = data[i]
                expected_crc = self._crc(data[i-2:i])
                if received_crc != expected_crc:
                    raise I2cChecksumError(received_crc, expected_crc, data)
        return words if len(words) > 0 else None

    @staticmethod
    def _build_tx_data(command, command_bytes, tx_words, crc):
        """
        Build the raw bytes to send from given command and words.

        :param command: See
            :py:meth:`~sensirion_i2c_driver.sensirion_word_command.__init__`.
        :param command_bytes: See
            :py:meth:`~sensirion_i2c_driver.sensirion_word_command.__init__`.
        :param tx_words: See
            :py:meth:`~sensirion_i2c_driver.sensirion_word_command.__init__`.
        :param crc: See
            :py:meth:`~sensirion_i2c_driver.sensirion_word_command.__init__`.
        :return:
            The raw bytes to send, or None if no write header is needed.
        :rtype:
            bytes/None
        """
        if (command is None) and (tx_words is None):
            return None
        command_pack_format = {
            1: ">B",
            2: ">H",
        }
        data = bytearray(pack(command_pack_format[command_bytes], command)
                         if command is not None else b"")
        for word in tx_words or []:
            raw_data = bytearray(pack(">H", word))
            data.extend(raw_data)
            if crc is not None:
                data.append(crc(raw_data))
        return data
