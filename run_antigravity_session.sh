#!/usr/bin/env bash
SESSION_ID="session_$(date +%s)_$RANDOM"
echo "Starting Antigravity with Session ID: $SESSION_ID"

# Export routing and tracking headers
export GEMINI_API_BASE="http://localhost:8080"
export GOOGLE_GENAI_BASE_URL="http://localhost:8080"
export CUSTOM_HEADERS="X-Antigravity-Session-ID: $SESSION_ID,X-Critic-Guard: strict,X-Hardening-Tier: maximum"
export HTTP_HEADER_X_ANTIGRAVITY_SESSION_ID="$SESSION_ID"

# Export Hardening & Invariant Inforcement for current session
export ANSE_HARDENED_GATE="1"
export ANSE_GATEWAY_CRITIC_ENABLED="1"
export ANSE_FAIL_CLOSED="1"
export HYPOTHESIS_PROFILE="ci"
export MUTATION_PROFILE="ci"
export ANTI_STUB_RIGOR="strict"
export PYTHONPATH="."

# Run Antigravity CLI command
antigravity "$@"
