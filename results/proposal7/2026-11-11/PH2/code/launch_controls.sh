#!/bin/bash
cd "$(dirname "$0")/.."
exec taskset -c 2 sage --python3 code/controls.py logs/controls.json
