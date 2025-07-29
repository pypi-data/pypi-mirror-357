# SnoScience

The source code, documentation, and CI/CD scripts for the SnoScience package are stored in this repository.

### Installation

1. Clone the repository with the following command:

```shell
git clone https://snomax@dev.azure.com/snomax/SnoScience/_git/SnoScience
```

2. Create a virtual environment and activate it.

3. Install poetry:

```shell
pip install poetry
```

4. Install the package with 'dev' and 'docs' dependency groups:

```shell
poetry install --with dev,docs
```

Optionally, add the 'validate' dependency group to install Tensorflow and Matplotlib. 

### Documentation

All documentation related to the usage and development of the SnoScience package can be found [here](https://thesecondsnomax.github.io/SnoScience/).
