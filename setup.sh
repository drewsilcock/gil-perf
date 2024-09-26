#!/bin/bash

set -euo pipefail

function info() {
    printf '\E[34m'; printf "[Info] "; printf '\E[0m'; echo "$@"
}

if ! command -v pyenv &> /dev/null; then
    if command -v brew &> /dev/null; then
        info "Installing pyenv from brew"
        brew install pyenv
    else
        info "Installing pyenv from pyenv.run"
        curl https://pyenv.run | bash
    fi

    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"

    info "Installed pyenv"
else
    info "Found existing pyenv installation"
fi

python_versions=(3.12.6 3.13.0rc2 3.13.0rc2t)

for python_version in "${python_versions[@]}"; do
    info "Installing Python $python_version"
    pyenv install -s $python_version
done

for python_version in "${python_versions[@]}"; do
    info "Creating venv for Python $python_version"
    export PYENV_VERSION=$python_version
    python -m venv .venv-$PYENV_VERSION
    source .venv-$PYENV_VERSION/bin/activate

    info "Installing dependencies for Python $python_version"
    poetry install
    deactivate
done

info "Done"
