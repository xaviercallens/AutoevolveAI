#!/usr/bin/env bash
SESSION_ID="session_$(date +%s)_$RANDOM"
echo "Starting Antigravity with Session ID: $SESSION_ID"

# Export routing and tracking headers
export GEMINI_API_BASE="http://localhost:8080"
export GOOGLE_GENAI_BASE_URL="http://localhost:8080"
export CUSTOM_HEADERS="X-Antigravity-Session-ID: $SESSION_ID"
export HTTP_HEADER_X_ANTIGRAVITY_SESSION_ID="$SESSION_ID"

# Run Antigravity CLI command
antigravity "$@"
