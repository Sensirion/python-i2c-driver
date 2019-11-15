# Python Driver for I2C Devices

This repository contains the common I2C driver used by various Sensirion
sensor drivers. For details, please read the package description in
[README.rst](README.rst).


## Usage

See package description in [README.rst](README.rst).


## Development

### Check coding style

The coding style can be checked with [`flake8`](http://flake8.pycqa.org/):

```bash
pip install -e .[test]  # Install requirements
flake8                  # Run style check
```

### Run tests

Unit tests can be run with [`pytest`](https://pytest.org/):

```bash
pip install -e .[test]          # Install requirements
pytest                          # Run tests
```

### Build documentation

The documentation can be built with [Sphinx](http://www.sphinx-doc.org/):

```bash
python setup.py install                        # Install package
pip install -r docs/requirements.txt           # Install requirements
sphinx-versioning build docs docs/_build/html  # Build documentation
```


## License

See [LICENSE](LICENSE).
