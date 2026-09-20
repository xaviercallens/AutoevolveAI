# PowerShell session wrapper for Antigravity with Intercept Gateway
$timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$randomVal = Get-Random -Minimum 1000 -Maximum 9999
$sessionId = "session_${timestamp}_${randomVal}"
Write-Host "Starting Antigravity with Session ID: $sessionId" -ForegroundColor Cyan

$env:GEMINI_API_BASE = "http://localhost:8080"
$env:GOOGLE_GENAI_BASE_URL = "http://localhost:8080"
$env:CUSTOM_HEADERS = "X-Antigravity-Session-ID: $sessionId"
$env:HTTP_HEADER_X_ANTIGRAVITY_SESSION_ID = "$sessionId"

# Run Antigravity CLI command
agy $args
