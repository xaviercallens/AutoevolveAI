# SuperGravity Integration Guide

This guide explains how to integrate **SuperGravity** into any existing repository, agentic workflow, or CI/CD pipeline to eliminate phantom completions, stubs, and simulated data.

---

## 📋 Integration Options

SuperGravity can be adopted progressively across three layers:
1. **Developer Workstation / Pre-Commit Hook**: Instant feedback preventing stubs and mock data from entering Git history.
2. **Autonomous Agent Gateway**: Intercepts LLM calls (Antigravity, Claude, Cursor) to enforce multi-tier routing and log audit streams to Redis.
3. **CI/CD Quality Gate**: Rejects PRs that lack cryptographic execution attestation or fail the 5-Gate Hardened Quality Pipeline.

---

## 🛠️ 1. Standalone Repository Drop-In (5 Minutes)

You can copy the core SuperGravity enforcement modules directly into your project:

### Required Core Files
```
your-repo/
├── execution_attestation.py    # Zero-trust AST & execution proof gate
├── context_manager.py          # Ephemeral context pruner (>60 lines)
├── antigravity_guard.py        # Phantom import and AST integrity scanner
└── .antigravity/
    └── hooks/
        └── hardened_gate.py    # 5-gate pipeline (Radon, Ruff, Bandit, Vulture, MyPy)
```

### Git Pre-Commit Hook Setup
Add the following to your `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: supergravity-attestation
        name: SuperGravity Anti-Stub & Anti-Simulation Gate
        entry: python execution_attestation.py
        language: system
        pass_filenames: false
        stages: [commit]
      - id: supergravity-hardened-gate
        name: SuperGravity 5-Gate Quality Pipeline
        entry: python .antigravity/hooks/hardened_gate.py
        language: system
        pass_filenames: false
        stages: [push]
```

Install the hooks:
```bash
pip install pre-commit
pre-commit install --hook-type pre-commit --hook-type pre-push
```

Now, any attempt to commit `pass` stubs, `...`, `NotImplementedError`, or fake variables (`mock_user = ...`) will be automatically blocked at commit time!

---

## 🌐 2. Multi-Tier Gateway Integration for LLM Agents

If your team uses autonomous agents (Google Antigravity CLI, Claude Code, Cursor, Aider, OpenHands), route their traffic through the SuperGravity gateway.

### Docker Compose Deployment
Add this service to your `docker-compose.yml`:
```yaml
services:
  supergravity-gateway:
    image: python:3.11-slim
    working_dir: /app
    volumes:
      - ./gateway.py:/app/gateway.py
      - ./context_manager.py:/app/context_manager.py
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - UPSTREAM_GEMINI_URL=https://generativelanguage.googleapis.com
      - MODEL_PLANNING=gemini-3.1-pro
      - MODEL_EXECUTION=gemini-3.8-flash
      - MODEL_VERIFICATION=gemini-3.1-pro
      - LOCAL_INFERENCE_URL=http://vllm:8000/v1/chat/completions
    command: >
      sh -c "pip install fastapi uvicorn httpx redis && uvicorn gateway:app --host 0.0.0.0 --port 8080"
    ports:
      - "8080:8080"
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### Configuring Agent CLIs
Direct your agent to use the gateway by exporting the environment variable:
```bash
# For Google Antigravity / Gemini SDK:
export GEMINI_API_BASE=http://localhost:8080

# For OpenAI-compatible agents (Cursor, Claude, Aider):
export OPENAI_BASE_URL=http://localhost:8080/v1

# For Anthropic Claude Code CLI:
export ANTHROPIC_BASE_URL=http://localhost:8080
```

The gateway automatically:
1. Inspects the semantic intent of prompts or `X-Task-Phase` headers.
2. Routes planning and review requests to **Gemini 3.1 Pro** for superior reasoning.
3. Routes code writing to **Gemini 3.8 Flash** for $4\times$ lower latency and lower token cost.
4. Transparently intercepts Anthropic `/v1/messages` and OpenAI `/v1/chat/completions` calls targeting `claude-3-5-sonnet` and `claude-3-opus`.
5. Logs every request, token count, latency, and response to Redis streams (`gateway:stream`, `gateway:claude_opus_dpo`) for preference harvesting.
6. Falls back to local GPU / vLLM if the upstream API hits rate limits.

### Harvesting Claude/Opus DPO Preference Datasets
To extract high-quality pairwise preferences logged by the gateway into HuggingFace/JSONL format:
```bash
# Export and validate pairwise RL preference records
uv run python scripts/export_claude_opus_rl_dataset.py \
  --output data/claude_opus_dpo_dataset.jsonl \
  --redis-host localhost \
  --redis-port 6379
```

---

## 🤖 3. Claude Workflow & MCP Integration

SuperGravity includes a Model Context Protocol (MCP) server allowing Claude Desktop or any MCP-enabled agent to access the guard:

```bash
# Run the MCP Guard Server
python mcp_guard_server.py
```

Configure in Claude Desktop (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "supergravity-guard": {
      "command": "python",
      "args": ["/path/to/SuperGravity/mcp_guard_server.py"]
    }
  }
}
```

The agent gains access to:
- `audit_code_changes`: Verifies that modified code has zero stubs.
- `attest_execution`: Runs tests with coverage tracing and mints cryptographic completion tokens.
- `offload_context`: Prunes verbose outputs to keep the context window sharp.

---

## 🎮 5. Antigravity Swarm Command Deck (ASCD) Control Center

The **Antigravity Swarm Command Deck (ASCD)** is the real-time operational user interface and telemetry dashboard for ANSE swarm nodes, Lean 4 provers, and execution engines.

### Running the Web Server
Launch the ASCD web application locally:
```bash
PORT=5000 uv run python web/server.py
```
Open your browser at `http://localhost:5000` to access the Control Center.

### REST API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/ascd/telemetry` | `GET` | Fetches live swarm telemetry, CPU/VRAM load, active MCP servers, and execution stats. |
| `/api/ascd/reset` | `POST` | **Atomic Control Center State Reset**: Restores baseline HUD telemetry, re-arms all 5 MCP servers, resets DAG execution nodes, flushes active stress testing, and purges execution log streams without requiring a server restart. |
| `/api/ascd/halt` | `POST` | Triggers emergency swarm circuit breaker and halts all running execution workers. |

### Web & Mobile Control Center UI State Reset Protocol

The ASCD Control Center features a unified, responsive user interface engineered for both high-resolution workstations (1920×1080) and mobile touch viewports (375×812):

1. **Header Action Bar**:
   - The `#ascd-btn-reset` button is positioned in the hero action bar.
   - On mobile screens ($\le 768\text{px}$), the action bar automatically wraps, maintaining a minimum $44\times44\text{px}$ touch target conforming to mobile accessibility standards.

2. **Client-Side Reset Workflow (`window.ascdResetDeck()`)**:
   - **Step 1: Network Request**: Dispatches `POST /api/ascd/reset` to synchronize baseline state on the backend.
   - **Step 2: HUD & Telemetry Reset**: Resets system load counters (VRAM: 1.2 GB / 24.0 GB, CPU: 12%, Active Nodes: 8).
   - **Step 3: Stress Engine Halt**: Cancels active stress loops (`isStressRunning = false`) and restores baseline pulse animations.
   - **Step 4: Tool & MCP Restoration**: Re-enables all 5 MCP server toggles (`antigravity-guard`, `lean4-prover`, `benchmark-runner`, `redis-telemetry`, `sandbox-evaluator`) to active state.
   - **Step 5: DAG & Log Purge**: Resets the reactive execution graph to baseline node states and clears the real-time streaming terminal logs.
   - **Step 6: Deck Navigation**: Switches the view smoothly back to Deck 1 (Swarm Command Overview) and triggers an amber confirmation HUD toast.

---

## 🚀 4. GitHub Actions CI/CD Pipeline

Add `.github/workflows/supergravity-gate.yml` to your repository:
```yaml
name: SuperGravity Zero-Trust Gate

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Dependencies
        run: |
          pip install uv
          uv pip install --system -e .
          uv pip install --system radon ruff bandit vulture mypy pytest pytest-cov

      - name: Run Anti-Stub & Anti-Simulation Attestation
        run: python execution_attestation.py

      - name: Run 5-Gate Hardened Quality Pipeline
        run: python .antigravity/hooks/hardened_gate.py

      - name: Run Full Test Suite with Coverage
        run: pytest tests/ --cov=. --cov-report=xml
```

---

## 💡 Troubleshooting & FAQs

### Q: Why did the attestation gate reject my PR with "Hardcoded synthetic data detected"?
**A**: SuperGravity detects variables starting with `mock_`, `dummy_`, `fake_`, `sample_`, or `test_data_` in **production** code. If you are writing mock fixtures, keep them inside the `tests/` directory where the rule is waived. Production code must retrieve or construct real runtime data.

### Q: Why was my function flagged as a stub?
**A**: The function contains only a docstring, `pass`, `...`, or `raise NotImplementedError`. Implement the real functional logic or remove the incomplete declaration.

### Q: Can I customize the cyclomatic complexity threshold?
**A**: Yes, the default threshold in `.antigravity/hooks/hardened_gate.py` is `MAX_CC = 10`. You can adjust this threshold in your local hook configuration if your architecture allows higher complexity functions.
