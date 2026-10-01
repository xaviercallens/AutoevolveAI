#!/bin/bash
# Release all GCP resources created by xautoresearch runner or benchmark scripts
# Usage: bash scripts/gcp_release_resources.sh

PROJECT="gen-lang-client-0625573011"
echo "=== Checking and releasing GCP compute resources on project $PROJECT ==="

gcloud compute instances list --project="$PROJECT" --filter='tags.items=xautoresearch' --format='get(name,zone)' | while read -r name zone; do
  if [ -n "$name" ] && [ -n "$zone" ]; then
    echo "Deleting $name in $zone..."
    gcloud compute instances delete "$name" --zone="$zone" --project="$PROJECT" --quiet
  fi
done

echo "Listing remaining compute instances on $PROJECT:"
gcloud compute instances list --project="$PROJECT"

echo "=== Resource release check complete. Running cost = $0. ==="
