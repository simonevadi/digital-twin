#!/bin/bash

. .venv/bin/activate

# Get the directory of the bash script
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

# Start IPython with the specified profile and matplotlib settings
ipython --profile=raypyng --matplotlib=qt5 --ipython-dir="$SCRIPT_DIR" "$@"
