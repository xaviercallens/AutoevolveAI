#!/bin/bash
# Release all GCP resources created by xautoresearch runner
# Run after all experiments are complete
gcloud compute instances list --filter='tags.items=xautoresearch' --format='get(name,zone)' | while read name zone; do
  if [ -n "$name" ] && [ -n "$zone" ]; then
    echo "Deleting $name in $zone..."
    gcloud compute instances delete "$name" --zone="$zone" --quiet
  fi
done
echo "All xautoresearch VMs deleted. Cost = $0."
