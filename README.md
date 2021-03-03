# dikort

Commit message format checking tool

python3 -m venv .venv
. ./.venv/bin/activate
pip install setuptools wheel
pip install -e '.[dev]'
docker build . -t test

## git hooks

ln -s -r -t ./.git/hooks/ ./hooks/*
