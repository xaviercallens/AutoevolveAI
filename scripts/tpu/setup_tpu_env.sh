#!/usr/bin/env bash
# Create the JAX/TPU venv (~/venv-tpu) on a Cloud TPU VM and auto-activate it in ~/.bashrc.
# Run ON the TPU VM, or remotely:
#   gcloud compute tpus tpu-vm ssh NAME --zone=ZONE --internal-ip --command="$(cat scripts/tpu/setup_tpu_env.sh)"
# Idempotent. Prints the backend and devices JAX actually sees; exits non-zero if it is not "tpu".
set -euo pipefail
VENV="$HOME/venv-tpu"
if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV" 2>/dev/null || { sudo apt-get install -y "python$(python3 -c 'import sys;print("%d.%d"%sys.version_info[:2])')-venv" >/dev/null && rm -rf "$VENV" && python3 -m venv "$VENV"; }
fi
. "$VENV/bin/activate"
pip -q install -U pip
pip -q install "jax[tpu]" -f https://storage.googleapis.com/jax-releases/libtpu_releases.html
grep -q venv-tpu "$HOME/.bashrc" || printf '\n# auto-activate JAX TPU env\n[ -f "$HOME/venv-tpu/bin/activate" ] && . "$HOME/venv-tpu/bin/activate"\n' >> "$HOME/.bashrc"
# CPU-only XLA flags in /etc/environment crash jaxlib on import; refuse to continue silently.
if grep -q 'xla_tpu' /etc/environment 2>/dev/null; then echo "WARNING: xla_tpu flags in /etc/environment" >&2; fi
python - <<'PY'
import sys, jax
print(jax.__version__, jax.default_backend(), jax.devices())
sys.exit(0 if jax.default_backend() == "tpu" else 1)
PY
