#!/bin/bash
# ==============================================================================
# Symbiotic Reality Engine Interceptor
# Usage: ./symbiotic_interceptor.sh <your test command>
# Example: ./symbiotic_interceptor.sh pytest tests/phase1
# ==============================================================================

TEST_CMD="$@"
if [ -z "$TEST_CMD" ]; then
    echo "Usage: ./symbiotic_interceptor.sh <test_command>"
    exit 1
fi

echo "🧪 [Symbiotic Engine] Executing Reality Harness..."
echo "Command: $TEST_CMD"
echo "--------------------------------------------------------------------------------"

# Run the command and capture output & exit code
OUTPUT=$(eval "$TEST_CMD" 2>&1)
EXIT_CODE=$?

echo "$OUTPUT"
echo "--------------------------------------------------------------------------------"

if [ $EXIT_CODE -eq 0 ]; then
    echo "🟢 [Energy = 0] Validation Passed!"
    echo "Updating AI synapses (Shadow Mode)..."
    uv run python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path().resolve()))
from harness_hook import record_golden_signal_dpo

record_golden_signal_dpo(
    prompt='Background Shadow Mode Validation',
    chosen_code='[Validated Local State]',
    rejected_code='[N/A]',
    metadata={'command': '$TEST_CMD', 'energy': 0.0, 'status': 'success'}
)
"
    echo "✅ Knowledge absorbed."
else
    echo "🔴 [Energy = 100] Validation Failed."
    echo "Injecting error trace into the AI's System 2 pondering loop..."
    
    # We escape single quotes for the inline python execution
    ESCAPED_OUTPUT=$(echo "$OUTPUT" | head -n 50 | sed "s/'/\\\\'/g")
    
    uv run python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path().resolve()))
from harness_hook import record_golden_signal_dpo

record_golden_signal_dpo(
    prompt='Harness Failure Trace',
    chosen_code='[Pending Human Fix]',
    rejected_code='''$ESCAPED_OUTPUT''',
    metadata={'command': '$TEST_CMD', 'energy': 100.0, 'status': 'failed'}
)
"
    echo "⚠️ Penalty recorded. AI is pondering the failure."
fi

exit $EXIT_CODE
