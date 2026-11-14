#!/bin/bash
set -u
D=/mnt/disks/disk-socrateai-local-1/callensxavier_home_data
T=$D/comparator_tools
export ELAN_HOME=$D/elan
export PATH=$ELAN_HOME/toolchains/leanprover--lean4---v4.34.1/bin:$T/bin:$PATH
export COMPARATOR_LANDRUN=$T/bin/landrun
export COMPARATOR_LEAN4EXPORT=$T/lean4export/.lake/build/bin/lean4export
cd $D/openai_math_pinned/lean
echo "== config $1"; cat $1
echo "== run"; time lake env $T/comparator/.lake/build/bin/comparator $1 2>&1 | grep -v "has local changes" | tail -40
echo "exit-of-pipeline: done"
