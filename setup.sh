#!/bin/bash

set -euxo pipefail

if ! command -v pyenv &> /dev/null; then
    if command -v brew &> /dev/null; then
        brew install pyenv
    else
        curl https://pyenv.run | bash
    fi

    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
fi

python_versions=(3.12.6 3.13.0rc2 3.13.0rc2t)

for python_version in "${python_versions[@]}"; do
    pyenv install -s $python_version
done

for python_version in "${python_versions[@]}"; do
    export PYENV_VERSION=$python_version
    python -m venv .venv-$PYENV_VERSION
    source .venv-$PYENV_VERSION/bin/activate
    poetry install
    deactivate
done
