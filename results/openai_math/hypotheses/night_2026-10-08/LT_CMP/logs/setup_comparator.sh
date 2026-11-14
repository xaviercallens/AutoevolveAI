#!/bin/bash
set -u
D=/mnt/disks/disk-socrateai-local-1/callensxavier_home_data
T=$D/comparator_tools
mkdir -p $T/bin
export ELAN_HOME=$D/elan
export PATH=$T/go/bin:$T/bin:$ELAN_HOME/bin:$PATH
cd $T
echo "== go"
if [ ! -x $T/go/bin/go ]; then
  V=$(curl -fsSL "https://go.dev/VERSION?m=text" | head -1)
  echo "go version $V"
  curl -fsSL "https://go.dev/dl/$V.linux-amd64.tar.gz" -o go.tgz && tar -xzf go.tgz && rm go.tgz
fi
go version
echo "== landrun"
[ -d landrun ] || git clone --depth 1 https://github.com/Zouuup/landrun.git
(cd landrun && GOBIN=$T/bin go install ./cmd/landrun && git rev-parse HEAD)
ls -la $T/bin
echo "== lean4export"
[ -d lean4export ] || git clone https://github.com/leanprover/lean4export.git
(cd lean4export && git rev-parse HEAD && cat lean-toolchain && git tag | tail -5)
echo "== comparator"
[ -d comparator ] || git clone https://github.com/leanprover/comparator.git
(cd comparator && git rev-parse HEAD && cat lean-toolchain && git tag | tail -5)
