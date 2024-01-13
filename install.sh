#!/bin/bash

THIS_SCRIPT_PATH=$(cd `dirname ${BASH_SOURCE[0]}` && pwd)
cd $THIS_SCRIPT_PATH

mkdir -p temp

# Install RAY-UI (not in use at the moment)
# pushd temp
# wget https://www.helmholtz-berlin.de/media/media/spezial/ray-ui/development/Ray-UI-development-Linux-installer
# chmod 755 Ray-UI-development-Linux-installer
# ./Ray-UI-development-Linux-installer
# popd

sudo apt install xvfb

git submodule update --init --recursive

python3 -m venv .venv
. .venv/bin/activate

pip install -e ./raypyng
pip install -e ./raypyng_bluesky

ln -s $(pwd)/profile_raypyng ~/.ipython/profile_raypyng



