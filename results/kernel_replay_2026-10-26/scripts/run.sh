TC=/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/elan/toolchains/leanprover--lean4---v4.34.1/bin
D=/tmp/kr_forged
mkdir -p $D/lib
export LEAN_PATH="$D/lib:$(cat /tmp/leanpath.txt)"
cd $D
echo "--- compile (lean -o)"
$TC/lean --root=$D/src -o $D/lib/KRForged.olean -i $D/lib/KRForged.ilean $D/src/KRForged.lean
echo "compile rc=$?"
echo "--- leanchecker KRForged"
timeout 900 $TC/leanchecker KRForged
echo "leanchecker rc=$?"
