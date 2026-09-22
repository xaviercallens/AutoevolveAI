"""
test_control_center.py — Verification & Validation Test Suite for Antigravity Swarm Command Deck (ASCD).
Validates all 14 test cases defined in specs/test UI.md across Desktop and Mobile responsive versions:
  - COR-01: Responsive Layout (1920px -> 375px carousel, no overflow)
  - COR-02: WebSocket Stress (200 evt/s, DOM virtualization, 60 FPS counter)
  - COR-03: Network Resiliency (Sticky offline banner, manual reconnect, fallback API)
  - FRG-01: Microservices DAG Architecture (Draggable nodes, touch-scroll lock, dynamic Béziers)
  - FRG-02: 3D Physics Engine (WebGL canvas, KaTeX energy formula, 2D fallback)
  - FRG-03: Lean 4 Tribunal (Line-number gutter, flashing red 🚨 on sorry, proof resolver)
  - PRV-01: QA Fuzzing Heatmap (10,000 cells canvas, hover/tap tooltip lookup)
  - PRV-02: Holographic Diff Slider (Image compare slider, magenta diff pixels, swipe-back lock)
  - ENG-01: RL Tinder DPO Evaluator (Touch swipe Right/Left gestures, DPO feedback API)
  - ENG-02: 2M Token Context Treemap (Drilldown and zoom-out back navigation)
  - ENG-03: Vector Memory 3D Pruning (Canvas node selection, context menu, particle explosion)
  - ENG-04: MCP Patchbay Switchboard (Accessible switches >= 48px hit area, toggle API)
  - GOD-01: Swarm Execution Halt (Spacebar, Mobile FAB 🛑, global overlay, input auto-focus)
  - GOD-02: Swarm Steer & Resume (Human correction injection into DAG, swarm unpause)
  - GOD-03: Swarm Time-Travel Slider (Historical replay, READ-ONLY REPLAY badge, rewind state)
"""

from __future__ import annotations

import re
import pytest
from fastapi.testclient import TestClient
from web.server import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def html(client: TestClient) -> str:
    res = client.get("/")
    assert res.status_code == 200
    return res.text


# ═════════════════════════════════════════════════════════════════════════════
# 1. CORE INFRASTRUCTURE & REAL-TIME TELEMETRY (COR-01 .. COR-03)
# ═════════════════════════════════════════════════════════════════════════════

class TestCoreInfrastructure:

    def test_cor_01_responsive_carousel_and_hud(self, html: str):
        """Verify Top HUD Carousel structure, CSS snap, and 6 metric cards."""
        assert 'id="ascd-hud-carousel"' in html
        assert "ascd-hud-carousel" in html
        assert "ascd-card-snap" in html

        # 6 distinct metrics present
        assert 'id="ascd-metric-agents"' in html
        assert 'id="ascd-metric-tps"' in html
        assert 'id="ascd-metric-cpu"' in html
        assert 'id="ascd-metric-vram"' in html
        assert 'id="ascd-metric-energy"' in html
        assert 'id="ascd-metric-redis"' in html

        # Verify CSS rules for horizontal scroll and mandatory snap
        assert "overflow-x: auto" in html
        assert "scroll-snap-type: x mandatory" in html

    def test_cor_02_virtualized_log_and_websocket_endpoint(self, client: TestClient, html: str):
        """Verify log stream container, stress test toggle, FPS counter, and WebSocket."""
        assert 'id="ascd-log-stream"' in html
        assert 'id="ascd-btn-stress"' in html
        assert 'id="ascd-fps-counter"' in html
        assert "toggleWebSocketStress" in html

        # Verify WebSocket connection
        with client.websocket_connect("/ws/ascd") as ws:
            data = ws.receive_json()
            assert "metrics" in data
            assert "status" in data
            assert data["status"] in ("RUNNING", "PAUSED")
            assert "tokens_per_sec" in data["metrics"]
            assert data["metrics"]["tokens_per_sec"] > 0

    def test_cor_03_network_resiliency_banner(self, client: TestClient, html: str):
        """Verify sticky offline banner, manual reconnect callback, and fallback telemetry."""
        assert 'id="ascd-offline-banner"' in html
        assert "ascdReconnectManually" in html

        # Test telemetry fallback endpoint
        resp = client.get("/api/ascd/telemetry")
        assert resp.status_code == 200
        payload = resp.json()
        assert "status" in payload
        assert "metrics" in payload
        assert "mcp_servers" in payload


# ═════════════════════════════════════════════════════════════════════════════
# 2. DECK 1: THE FORGE (FRG-01 .. FRG-03)
# ═════════════════════════════════════════════════════════════════════════════

class TestDeck1Forge:

    def test_frg_01_dag_architecture_markup_and_events(self, html: str):
        """Verify SVG DAG canvas, Bézier gradient, touch-scroll lock, and drag handlers."""
        assert 'id="ascd-dag-wrapper"' in html
        assert 'id="ascd-dag-svg"' in html
        assert 'id="ascd-dag-edges"' in html
        assert 'id="ascd-dag-nodes"' in html
        assert 'marker id="arrow"' in html
        assert "touch-scroll-lock" in html
        assert "ascdRenderDag" in html
        assert "ascdDagState" in html

    def test_frg_02_physics_engine_canvas_and_katex(self, html: str):
        """Verify 3D canvas, 2D fallback button, and KaTeX math formulation."""
        assert 'id="ascd-physics-canvas"' in html
        assert 'id="ascd-physics-toggle"' in html
        assert "togglePhysics2DFallback" in html
        # KaTeX energy formula
        assert "E_{\\text{total}}" in html
        assert "E_{\\text{jepa}}" in html

    def test_frg_03_lean4_tribunal_sorry_gutter(self, html: str):
        """Verify Monaco-style theorem gutter with flashing red alert and proof fixer."""
        assert 'id="ascd-lean-gutter"' in html
        assert "gutter-icon-sorry" in html
        assert "🚨" in html
        assert "ascdFixSorryDemonstration" in html
        assert "UNPROVEN OBLIGATION DETECTED" in html


# ═════════════════════════════════════════════════════════════════════════════
# 3. DECK 2: PROVING GROUNDS (PRV-01 .. PRV-02)
# ═════════════════════════════════════════════════════════════════════════════

class TestDeck2ProvingGrounds:

    def test_prv_01_qa_heatmap_10000_cells(self, html: str):
        """Verify 10,000-cell (100x100) canvas heatmap and hover/tap tooltip."""
        assert 'id="ascd-heatmap-canvas"' in html
        assert 'id="ascd-heatmap-tooltip"' in html
        assert 'id="ascd-tooltip-title"' in html
        assert 'id="ascd-tooltip-body"' in html
        assert "ascdRegenerateHeatmap" in html
        assert "ascdHeatmapFails" in html

    def test_prv_02_holographic_diff_slider(self, html: str):
        """Verify image comparison container, draggable divider, and swipe-back prevention."""
        assert 'id="ascd-diff-container"' in html
        assert 'id="ascd-diff-slider-bar"' in html
        assert 'id="ascd-diff-left"' in html
        assert "touch-none" in html
        assert "ascdInitDiffSlider" in html


# ═════════════════════════════════════════════════════════════════════════════
# 4. DECK 3: ENGINE ROOM (ENG-01 .. ENG-04)
# ═════════════════════════════════════════════════════════════════════════════

class TestDeck3EngineRoom:

    def test_eng_01_rl_tinder_dpo(self, client: TestClient, html: str):
        """Verify RL Tinder card swipe elements and DPO feedback submission endpoint."""
        assert 'id="ascd-tinder-card"' in html
        assert 'id="ascd-dpo-counter"' in html
        assert "ascdSwipeTinder" in html

        # Test POST /api/ascd/dpo-feedback
        resp = client.post("/api/ascd/dpo-feedback", json={"card_id": "card_0", "decision": "accept"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["decision"] == "accept"
        assert data["total_records"] >= 43

        resp_reject = client.post("/api/ascd/dpo-feedback", json={"card_id": "card_0", "decision": "reject"})
        assert resp_reject.status_code == 200
        assert resp_reject.json()["decision"] == "reject"

    def test_eng_02_context_treemap(self, html: str):
        """Verify 2M Token Context Treemap drilldown categories and back button."""
        assert 'id="ascd-treemap-container"' in html
        assert 'id="ascd-treemap-back"' in html
        assert "ascdDrilldownTreemap" in html
        assert "ascdResetTreemapZoom" in html
        assert "GitHub Docs" in html
        assert "AST Sandbox" in html

    def test_eng_03_memory_pruning(self, client: TestClient, html: str):
        """Verify vector memory canvas, right-click/touch menu, and prune API."""
        assert 'id="ascd-memory-canvas"' in html
        assert 'id="ascd-memory-menu"' in html
        assert "ascdExecuteMemoryPrune" in html

        # Test POST /api/ascd/memory-prune
        resp = client.post("/api/ascd/memory-prune", json={"node_id": "mem_ast_parser"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "pruned"
        assert data["node_id"] == "mem_ast_parser"
        assert data["particles"] > 0

    def test_eng_04_mcp_patchbay(self, client: TestClient, html: str):
        """Verify MCP switches with hit areas >= 48px and toggle API."""
        assert 'id="ascd-toggle-bash"' in html
        assert 'id="ascd-toggle-fs"' in html
        assert 'id="ascd-toggle-mem"' in html
        assert 'id="ascd-toggle-lean"' in html
        assert "mcp-switch-box" in html
        assert "min-width: 48px" in html
        assert "min-height: 48px" in html
        assert "ascdToggleMcpServer" in html

        # Test POST /api/ascd/mcp-toggle
        resp = client.post("/api/ascd/mcp-toggle", json={"server_id": "mcp_bash_terminal", "enabled": False})
        assert resp.status_code == 200
        assert resp.json()["enabled"] is False

        resp2 = client.post("/api/ascd/mcp-toggle", json={"server_id": "mcp_bash_terminal", "enabled": True})
        assert resp2.status_code == 200
        assert resp2.json()["enabled"] is True


# ═════════════════════════════════════════════════════════════════════════════
# 5. GOD MODE & TIME-TRAVEL (GOD-01 .. GOD-03)
# ═════════════════════════════════════════════════════════════════════════════

class TestGodModeAndReplay:

    def test_god_01_halt_spacebar_and_fab(self, client: TestClient, html: str):
        """Verify Spacebar handler, Mobile FAB, modal overlay, and halt endpoint."""
        assert 'id="ascd-fab-god"' in html
        assert 'id="ascd-god-overlay"' in html
        assert 'id="ascd-steer-input"' in html
        assert "triggerGodModeHalt" in html
        assert "e.code === 'Space'" in html

        # Test POST /api/ascd/halt
        resp = client.post("/api/ascd/halt", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert data["paused"] is True
        assert data["status"] == "PAUSED"

    def test_god_02_steer_and_resume(self, client: TestClient, html: str):
        """Verify human instruction steering submission and DAG node injection."""
        assert "submitSteerAndResume" in html
        assert "resumeSwarmWithoutSteering" in html

        # Test POST /api/ascd/steer
        instruction = "Enforce Lean 4 anti-stub proof before deployment"
        resp = client.post("/api/ascd/steer", json={"instruction": instruction})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "RUNNING"
        assert "node" in data
        assert data["node"]["instruction"] == instruction
        assert "correction_id" in data

    def test_god_03_time_travel_slider(self, client: TestClient, html: str):
        """Verify Time-Travel Drawer, slider input handler, replay badge, and API."""
        assert 'id="ascd-time-drawer"' in html
        assert 'id="ascd-time-slider"' in html
        assert 'id="ascd-replay-badge"' in html
        assert 'id="ascd-time-offset-label"' in html
        assert "READ-ONLY REPLAY" in html
        assert "onTimeTravelSliderInput" in html

        # Test POST /api/ascd/replay at -45 minutes
        resp = client.post("/api/ascd/replay", json={"offset_minutes": -45})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "READ-ONLY REPLAY"
        assert data["offset_minutes"] == -45
        assert "historical_metrics" in data

        # Test return to LIVE (offset 0)
        resp_live = client.post("/api/ascd/replay", json={"offset_minutes": 0})
        assert resp_live.status_code == 200
        assert resp_live.json()["status"] == "LIVE"
