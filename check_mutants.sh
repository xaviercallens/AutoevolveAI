#!/usr/bin/env bash
set -eo pipefail

echo "==> Running Mutmut with Hypothesis 'mutation' profile..."
export HYPOTHESIS_PROFILE=mutation
mutmut run

# Output status summary
mutmut results

# Check for surviving mutants
SURVIVING=$(mutmut results | grep -oE "[0-9]+ survived" | awk '{print $1}' || echo "0")

if [ "$SURVIVING" -gt 0 ]; then
    echo "❌ Quality Gate Failed: $SURVIVING mutant(s) survived."
    echo "Inspect with: mutmut show <id>"
    exit 1
fi

echo "✅ 100% Mutation score achieved! All properties killed injected mutants."
