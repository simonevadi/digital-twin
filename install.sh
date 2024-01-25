#!/bin/bash


sudo apt install xvfb

git submodule update --init --recursive

# python3 -m venv .venv
. .venv/bin/activate

pip install -e ./raypyng
pip install -e ./raypyng-bluesky
pip install -e ./beamlinetools


pip install ipython notebook twisted




