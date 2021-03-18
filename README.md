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

* Wide check list: author name, email, trailing periods, capitalize sentence, singleline summary, singoff, gpg, regex.
* Checks any commit range: acceptable for both CI and pre-commit hook usage
* Separate rules for both: merge and regular commits
* Support all available python versions: 3.6+

## Technical Requirements/Installation

### Pre-requirements
Install any supported python distribution (for now it's 3.6+), and pip package management tool. Also make sure you have git installed

Examples:

#### Ubuntu/Debian
```shell
sudo apt install python3 python3-pip git
```

#### CentOS/RedHat/Fedora
```shell
sudo yum install python3 git
```

### Installation

By default, pip tries to install package directly to you system. You may need to use sudo to achieve this

```shell
sudo pip3 install dikort
```

The more right way is to **install to your home directory**. But be sure you have `$HOME/.local/bin` at your `$PATH` variable 
```shell
pip3 install --user dikort
```

## Running and Configuring

Dikort is a command line tool. To see all available options with explanation hit `dikort -h`. 
The only one unnamed option is commit range in the notation of `"<commit1>..<commit2>"`, where `"commit1"` and `"commit2"` are any of:
hash, branch, tag, HEAD pointer.

### Examples

#### Check last commit. Use this in git pre-commit hook
```shell
dikort HEAD~1..HEAD
```

#### Check last 10 commits
```shell
dikort HEAD~10..HEAD
```

#### Check all commits in fix-123 branch
```shell
dikort master..fix-123
```

#### Configure through command line
```shell
dikort --enable-length --enable-capitalized-summary --min-length=20 --max-length=72 HEAD~5..HEAD
```

#### Get log and save it (DEBUG mode)
```shell
dikort --enable-logging --logging-level=DEBUG 2>debug.log
```

### Run in docker

Also you can run inside docker. Just mount your repository to container and tell dikort where to find.

```shell
docker run -v `pwd`:/tmp/repo weastur/dikort:latest --repository=/tmp/repo --enable-length
```

## File configuration

Refer to [config example](./dikort.example.cfg), as a full configuration file. By default, config searched at `./.dikort.cfg` 

## Development Status

Dikort is in active development and accepts contributions. See our [Contributing](#how-to-contribute) section below for more details.

We report new releases information [here](https://github.com/weastur/dikort/releases).

## How to contribute

Fork, clone, setup development environment. **No third-party build or test tools** need to be insttalled at your system.

```shell
python3 -m venv .venv
. ./.venv/bin/activate
pip install setuptools wheel
pip install -e '.[dev]'
```

After that you'll have dikort and all development tools installed into virtualenv. Just run here `dikort` to execute your development version.
Hack, then make PR. Don't forget to write unit tests, and check your code:

```shell
dikort
flake8 dikort
isort dikort
black dikort
coverage run -m unittest discover
coverage report
```

Or you can just install git-hooks

### Git hooks

```shell
ln -s -r -t ./.git/hooks/ ./hooks/*
```

## License

MIT, see [LICENSE](./LICENSE).
