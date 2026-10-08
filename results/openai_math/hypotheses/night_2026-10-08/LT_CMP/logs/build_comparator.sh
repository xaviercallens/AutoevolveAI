#!/bin/bash
set -u
D=/mnt/disks/disk-socrateai-local-1/callensxavier_home_data
T=$D/comparator_tools
export ELAN_HOME=$D/elan
export PATH=$T/go/bin:$T/bin:$ELAN_HOME/bin:$PATH
for r in lean4export comparator; do
  cd $T/$r
  echo "== $r: checkout v4.34.0"
  git checkout -q v4.34.0 && git rev-parse HEAD
  echo "leanprover/lean4:v4.34.1" > lean-toolchain
  echo "toolchain now: $(cat lean-toolchain)"
  cat lakefile* 2>/dev/null | head -30
done
cd $T/lean4export
echo "== build lean4export"; time lake build 2>&1 | tail -8
cd $T/comparator
echo "== build comparator"; time lake build 2>&1 | tail -8
ls -la $T/lean4export/.lake/build/bin $T/comparator/.lake/build/bin 2>&1
