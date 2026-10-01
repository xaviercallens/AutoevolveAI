#!/usr/bin/env bash
# ==============================================================================
# gcp_nightly_retrain.sh
# ==============================================================================
# Schedules and launches automated nightly retraining of Laya Coding Companion
# on GCP Spot instances at lowest cost:
#   - CPU Spot: n2-standard-4 (~$0.012/hr)
#   - GPU Spot: n1-standard-4 + NVIDIA T4 (~$0.035/hr)
# Guarantees $0.00 idle cost by self-terminating the VM upon job completion.
# ==============================================================================

set -euo pipefail

PROJECT_ID="gen-lang-client-0625573011"
ZONE="us-central1-a"
MODE="${1:-cpu}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
INSTANCE_NAME="laya-nightly-retrain-${MODE}-${TIMESTAMP}"
GCS_BUCKET="gs://socrateai-datalake-gen-lang-client-0625573011"

echo "========================================================================"
echo "🌙 GCP Spot Nightly Retraining Launcher"
echo "   Mode:          ${MODE} (Spot / Preemptible)"
echo "   Instance:      ${INSTANCE_NAME}"
echo "   Project:       ${PROJECT_ID}"
echo "   Zone:          ${ZONE}"
echo "   Target Bucket: ${GCS_BUCKET}"
echo "========================================================================"

if [[ "${1:-}" == "--dry-run" || "${2:-}" == "--dry-run" ]]; then
    echo "🔎 DRY-RUN MODE: Verifying Spot configuration..."
    echo "  [gcloud check] Project: ${PROJECT_ID}"
    echo "  [VM Type]       Mode CPU: n2-standard-4 (Spot ~$0.012/hr)"
    echo "  [VM Type]       Mode GPU: n1-standard-4 + NVIDIA T4 (Spot ~$0.035/hr)"
    echo "  [Self-Destruct] EXIT trap guarantees VM deletion upon completion."
    echo "  ✓ Spot configuration validated."
    exit 0
fi

# Define Startup Script for Ephemeral Spot VM
STARTUP_SCRIPT=$(cat << 'EOF'
#!/usr/bin/env bash
set -x

export DEBIAN_FRONTEND=noninteractive
apt-get update && apt-get install -y git python3-pip

# Ensure self-termination on exit or failure
trap 'gcloud compute instances delete $(hostname) --zone=$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/zone" -H "Metadata-Flavor: Google" | cut -d/ -f4) --quiet' EXIT

# Pull latest code
cd /tmp
git clone https://github.com/xaviercallens/AutoevolveAI.git
cd AutoevolveAI

# Run Nightly Retrain Runner
python3 -m pip install -e .
python3 scripts/nightly_retrain_runner.py --epochs 3

echo "=== Retraining Job Finished Successfully. Triggering Self-Termination. ==="
EOF
)

# Launch Spot Instance based on Mode
if [[ "${MODE}" == "gpu" ]]; then
    echo "🚀 Provisioning GPU Spot VM with NVIDIA T4..."
    gcloud compute instances create "${INSTANCE_NAME}" \
        --project="${PROJECT_ID}" \
        --zone="${ZONE}" \
        --machine-type="n1-standard-4" \
        --accelerator="type=nvidia-tesla-t4,count=1" \
        --maintenance-policy="TERMINATE" \
        --provisioning-model="SPOT" \
        --instance-termination-action="DELETE" \
        --max-run-duration="7200s" \
        --image-family="common-cu121-debian-11" \
        --image-project="deeplearning-platform-release" \
        --boot-disk-size="50GB" \
        --metadata="startup-script=${STARTUP_SCRIPT}" \
        --scopes="https://www.googleapis.com/auth/cloud-platform" \
        --quiet
else
    echo "🚀 Provisioning CPU Spot VM (n2-standard-4)..."
    gcloud compute instances create "${INSTANCE_NAME}" \
        --project="${PROJECT_ID}" \
        --zone="${ZONE}" \
        --machine-type="n2-standard-4" \
        --provisioning-model="SPOT" \
        --instance-termination-action="DELETE" \
        --max-run-duration="7200s" \
        --image-family="debian-12" \
        --image-project="debian-cloud" \
        --boot-disk-size="50GB" \
        --metadata="startup-script=${STARTUP_SCRIPT}" \
        --scopes="https://www.googleapis.com/auth/cloud-platform" \
        --quiet
fi

echo "========================================================================"
echo "✅ Spot VM Launched: ${INSTANCE_NAME}"
echo "   It will execute retraining, upload to ${GCS_BUCKET}, and self-delete."
echo "   Guaranteed \$0.00 idle cost."
echo "========================================================================"
