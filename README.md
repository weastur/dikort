[![Build Status](https://travis-ci.com/weastur/dikort.svg?branch=main)](https://travis-ci.com/weastur/dikort)
[![codecov](https://codecov.io/gh/weastur/dikort/branch/main/graph/badge.svg)](https://codecov.io/gh/weastur/dikort)
[![PyPi version](https://img.shields.io/pypi/v/dikort.svg)](https://pypi.org/project/dikort/)
[![Python versions](https://img.shields.io/pypi/pyversions/dikort)](https://pypi.org/project/dikort/)
[![black-formatter](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![visitors](https://visitor-badge.glitch.me/badge?page_id=weastur.dikort)

# Dikort: git commit message format checking tool

The tool that helps you make commit message in your repository clear.

## Key Features

* Wide check list: author name, email, trailing periods, capitalize sentence, singoff, gpg, regex.
* Check any commit range: acceptable for both CI and pre-commit hook usage
* Separate rules for both: merge and regular commits
* Support all available python versions: 3.6+

## Technical Requirements/Installation

### Pre-requirements
Install any supported python distribution (for now it's 3.6+), and pip package management tool.

Examples:

#### Ubuntu/Debian
```shell
sudo apt install python3 python3-pip
```

#### CentOS/RedHat/Fedora
```shell
sudo yum install python3
```

### Installation

By default, pip tries to install package directly to you system. You may need to use sudo to achieve this

```shell
sudo pip3 install dikort
```

The more accurate way is to install to your home directory. But be sure you have `$HOME/.local/bin` at your `$PATH` variable 
```shell
pip3 install --user dikort
```

## Running and Configuring

## File configuration

Refer to [config example](./dikort.example.cfg), as a full configuration file.

## Development Status

Dikort is in active development and accepts contributions. See our [Contributing](#how-to-contribute) section below for more details.

We report new releases information [here](https://github.com/weastur/dikort/releases).

## How to contribute

Fork, clone, setup development environment. No third-party tools need.

```shell
python3 -m venv .venv
. ./.venv/bin/activate
pip install setuptools wheel
pip install -e '.[dev]'
```

After that you'll have dikort and all development tools installed into virtualenv. Just run here `dikort` to execute your development version.
Hack, then make PR. Don't forget to write unit tests, and check your code with `flake8`, `isort`, `black`.   

## License

MIT, see [LICENSE](./LICENSE).
