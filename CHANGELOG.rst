CHANGELOG
---------

1.0.0
:::::
- First public release
- Add support for post processing time of commands
- Add property ``is_multi_channel`` to ``I2cConnection``
- Make API of ``SensirionWordI2cCommand`` byte-oriented
- Rename class ``SensirionWordI2cCommand`` to ``SensirionI2cCommand``
- Remove methods ``read()`` and ``write()`` from ``I2cConnection``
- Remove asynchronous mode (including the ``read()`` method) from ``I2cDevice``
- Log transceived raw data with ``log.debug()``
- Various documentation improvements

0.1.0
:::::
- Initial release
