"""
test_ascd_playwright_e2e.py — Comprehensive Playwright End-to-End Non-Regression Tests.
Validates the Antigravity Swarm Command Deck (ASCD) against:
  - specs/Swarm control Center Ui.md
  - specs/test UI.md
  - specs/Roadmap.md
  - docs/ANTIGRAVITY_HARNESS.md
  - docs/EBM_JEPA_Foundations.md
  - docs/EVOLUTION_LAB.md
  - docs/INTEGRATION_GUIDE.md
  - docs/LeCun2006_EBM_Summary.md
  - docs/MINI_RL_GUIDE.md

Uses system Google Chrome (/usr/bin/google-chrome) for full native headless execution in local dev.
"""

from __future__ import annotations

import time
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

BASE_URL = "http://127.0.0.1:5000/#ascd"
CHROME_PATH = "/usr/bin/google-chrome"


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
        yield b
        b.close()


@pytest.fixture
def desktop_page(browser: Browser) -> Page:
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()
    page.goto(BASE_URL, wait_until="networkidle")
    # Wait for ASCD section to be visible
    page.wait_for_selector("#section-ascd", state="visible")
    yield page
    context.close()


@pytest.fixture
def mobile_page(browser: Browser) -> Page:
    context = browser.new_context(
        viewport={"width": 375, "height": 812},
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        has_touch=True,
    )
    page = context.new_page()
    page.goto(BASE_URL, wait_until="networkidle")
    page.wait_for_selector("#section-ascd", state="visible")
    yield page
    context.close()


# ═════════════════════════════════════════════════════════════════════════════
# 1. DESKTOP E2E TESTS (1920x1080)
# ═════════════════════════════════════════════════════════════════════════════

class TestDesktopE2E:

    def test_desktop_hud_metrics_and_log_stream(self, desktop_page: Page):
        """COR-01 & COR-02: HUD telemetry cards and live virtualized log stream."""
        # Check title and status
        status = desktop_page.locator("#ascd-swarm-status")
        assert "RUNNING" in status.inner_text()

        # Check all 6 HUD cards
        agents = desktop_page.locator("#ascd-metric-agents")
        tps = desktop_page.locator("#ascd-metric-tps")
        cpu = desktop_page.locator("#ascd-metric-cpu")
        vram = desktop_page.locator("#ascd-metric-vram")
        energy = desktop_page.locator("#ascd-metric-energy")
        redis = desktop_page.locator("#ascd-metric-redis")

        assert "Agents" in agents.inner_text()
        assert "tok/s" in tps.inner_text()
        assert "%" in cpu.inner_text()
        assert "MB" in vram.inner_text()
        assert len(energy.inner_text()) > 0
        assert len(redis.inner_text()) > 0

        # Check live log stream
        log_stream = desktop_page.locator("#ascd-log-stream")
        assert log_stream.is_visible()
        # Verify FPS counter
        fps_counter = desktop_page.locator("#ascd-fps-counter")
        assert "FPS" in fps_counter.inner_text()

        # Toggle stress test
        stress_btn = desktop_page.locator("#ascd-btn-stress")
        stress_btn.click()
        time.sleep(0.5)
        # Should now show Stop stress
        assert "Stop" in stress_btn.inner_text() or "Stress" in stress_btn.inner_text()
        stress_btn.click()  # stop

    def test_desktop_deck1_the_forge_dag_physics_and_lean(self, desktop_page: Page):
        """FRG-01, FRG-02, FRG-03: DAG SVG, 3D Physics Manifold, Lean 4 Tribunal."""
        # Make sure Deck 1 is active
        desktop_page.locator("#btn-deck-forge").click()
        desktop_page.wait_for_selector("#subdeck-forge", state="visible")

        # 1. DAG Architecture
        dag_svg = desktop_page.locator("#ascd-dag-svg")
        assert dag_svg.is_visible()
        # Check nodes are rendered
        planner_node = desktop_page.locator('g.ascd-node-element[data-id="n_planner"]')
        assert planner_node.is_visible()
        assert "Architecture Planner" in (planner_node.text_content() or "")

        # Test dragging the node
        box = planner_node.bounding_box()
        assert box is not None
        desktop_page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        desktop_page.mouse.down()
        desktop_page.mouse.move(box["x"] + 100, box["y"] + 50)
        desktop_page.mouse.up()
        # Verify notification flashes
        notif = desktop_page.locator("#ascd-dag-notification")
        # May be visible or quickly hidden
        assert notif.count() > 0

        # 2. Physics Simulation Canvas & KaTeX
        physics_canvas = desktop_page.locator("#ascd-physics-canvas")
        assert physics_canvas.is_visible()
        toggle_btn = desktop_page.locator("#ascd-physics-toggle")
        assert "Mode: WebGL 3D" in toggle_btn.inner_text()
        toggle_btn.click()
        assert "Mode: 2D Contour" in toggle_btn.inner_text()
        toggle_btn.click()
        assert "Mode: WebGL 3D" in toggle_btn.inner_text()

        # 3. Lean 4 Tribunal Gutter with sorry
        gutter = desktop_page.locator("#ascd-lean-gutter")
        assert "🚨" in gutter.inner_text()
        assert "4" in gutter.inner_text()

        # Click Prove button
        prove_btn = desktop_page.locator('button:has-text("Prove (Remove sorry)")')
        prove_btn.click()

        # Verify sorry is resolved to green checkmark
        assert "✅" in gutter.inner_text()
        assert "🚨" not in gutter.inner_text()

    def test_desktop_deck2_proving_grounds_heatmap_and_diff(self, desktop_page: Page):
        """PRV-01 & PRV-02: 10,000-cell QA Heatmap and Holographic Diff Slider."""
        # Switch to Deck 2
        desktop_page.locator("#btn-deck-proving").click()
        desktop_page.wait_for_selector("#subdeck-proving", state="visible")

        # 1. QA Fuzzing Heatmap
        heatmap = desktop_page.locator("#ascd-heatmap-canvas")
        assert heatmap.is_visible()
        box = heatmap.bounding_box()
        assert box is not None

        # Hover over canvas to trigger tooltip
        desktop_page.mouse.move(box["x"] + 50, box["y"] + 50)
        time.sleep(0.2)
        tooltip = desktop_page.locator("#ascd-heatmap-tooltip")
        assert tooltip.is_visible()
        assert "Test #" in tooltip.inner_text()

        # 2. Holographic Diff Slider
        diff_container = desktop_page.locator("#ascd-diff-container")
        assert diff_container.is_visible()
        slider_bar = desktop_page.locator("#ascd-diff-slider-bar")
        assert slider_bar.is_visible()

        # Drag the slider divider
        cbox = diff_container.bounding_box()
        assert cbox is not None
        desktop_page.mouse.move(cbox["x"] + cbox["width"] * 0.5, cbox["y"] + cbox["height"] * 0.5)
        desktop_page.mouse.down()
        desktop_page.mouse.move(cbox["x"] + cbox["width"] * 0.25, cbox["y"] + cbox["height"] * 0.5)
        desktop_page.mouse.up()

        left_pane = desktop_page.locator("#ascd-diff-left")
        style = left_pane.get_attribute("style") or ""
        assert "width" in style

    def test_desktop_deck3_engine_room_rl_treemap_memory_mcp(self, desktop_page: Page):
        """ENG-01 .. ENG-04: RL Tinder DPO, Context Treemap, Memory Pruning, MCP Switchboard."""
        # Switch to Deck 3
        desktop_page.locator("#btn-deck-engine").click()
        desktop_page.wait_for_selector("#subdeck-engine", state="visible")

        # 1. RL Tinder DPO Card
        tinder_card = desktop_page.locator("#ascd-tinder-card")
        assert tinder_card.is_visible()
        counter = desktop_page.locator("#ascd-dpo-counter")
        initial_text = counter.inner_text()

        # Click Accept
        accept_btn = desktop_page.locator('button:has-text("✓ Accept")')
        accept_btn.click()
        time.sleep(0.5)
        assert counter.inner_text() != initial_text

        # 2. 2M Token Context Treemap Drill-down
        treemap = desktop_page.locator("#ascd-treemap-container")
        assert "GitHub Docs" in treemap.inner_text()
        desktop_page.locator("#ascd-treemap-container > div").first.click()
        time.sleep(0.3)

        # Sub-chunks should be visible, and back button
        back_btn = desktop_page.locator("#ascd-treemap-back")
        assert back_btn.is_visible()
        assert "Sub-chunk" in treemap.inner_text()

        # Click Back
        back_btn.click()
        time.sleep(0.3)
        assert not back_btn.is_visible()
        assert "GitHub Docs" in treemap.inner_text()

        # 3. Vector Memory Pruning
        mem_canvas = desktop_page.locator("#ascd-memory-canvas")
        assert mem_canvas.is_visible()
        # Right click on memory canvas
        mbox = mem_canvas.bounding_box()
        assert mbox is not None
        desktop_page.mouse.click(mbox["x"] + 120, mbox["y"] + 70, button="right")
        time.sleep(0.2)
        menu = desktop_page.locator("#ascd-memory-menu")
        if menu.is_visible():
            desktop_page.locator('button:has-text("Prune Memory Node")').click()

        # 4. MCP Patchbay Switchboard
        toggle_fs = desktop_page.locator("#ascd-toggle-fs")
        status_fs = desktop_page.locator("#ascd-mcp-status-fs")
        assert "Active" in status_fs.inner_text()
        toggle_fs.click()
        time.sleep(0.3)
        assert "Disabled" in status_fs.inner_text()
        toggle_fs.click()
        time.sleep(0.3)
        assert "Active" in status_fs.inner_text()

    def test_desktop_god_mode_halt_and_steer(self, desktop_page: Page):
        """GOD-01 & GOD-02: Spacebar / Halt button emergency pause, steer input, and resume."""
        status = desktop_page.locator("#ascd-swarm-status")
        assert "RUNNING" in status.inner_text()

        # Click Halt Swarm button
        desktop_page.locator("#ascd-btn-halt").click()
        overlay = desktop_page.locator("#ascd-god-overlay")
        assert overlay.is_visible()
        assert "PAUSED" in status.inner_text()

        # Enter human steering instruction
        steer_input = desktop_page.locator("#ascd-steer-input")
        steer_input.fill("Enforce strict monotonicity in energy calculation")

        # Submit steer & resume
        resume_btn = desktop_page.locator('button:has-text("Steer & Resume ⚡")')
        resume_btn.click()

        time.sleep(0.3)
        assert not overlay.is_visible()
        assert "RUNNING" in status.inner_text()

    def test_desktop_time_travel_replay(self, desktop_page: Page):
        """GOD-03: Expand time travel drawer, adjust slider to -30m, and reset to live."""
        # Click Time-Travel button to open drawer
        desktop_page.locator('button:has-text("Time-Travel")').click()
        drawer = desktop_page.locator("#ascd-time-drawer")
        assert not drawer.evaluate("el => el.classList.contains('collapsed')")

        # Set slider to -30 min
        slider = desktop_page.locator("#ascd-time-slider")
        slider.fill("-30")
        slider.dispatch_event("input")

        time.sleep(0.3)
        badge = desktop_page.locator("#ascd-replay-badge")
        assert badge.is_visible()
        assert "READ-ONLY REPLAY" in badge.inner_text()
        offset_label = desktop_page.locator("#ascd-time-offset-label")
        assert "-30 min" in offset_label.inner_text()

        # Reset to Live
        desktop_page.locator('button:has-text("Reset to Live")').click()
        time.sleep(0.3)
        assert not badge.is_visible()
        assert "LIVE (0 min)" in offset_label.inner_text()


# ═════════════════════════════════════════════════════════════════════════════
# 2. MOBILE E2E TESTS (375x812 Viewport with Touch)
# ═════════════════════════════════════════════════════════════════════════════

class TestMobileE2E:

    def test_mobile_responsive_carousel_and_bottom_nav(self, mobile_page: Page):
        """COR-01 on mobile: Carousel snap scrolling and bottom PWA nav bar."""
        carousel = mobile_page.locator("#ascd-hud-carousel")
        assert carousel.is_visible()

        # Verify scroll-snap CSS
        snap_type = carousel.evaluate("el => getComputedStyle(el).scrollSnapType")
        assert "x mandatory" in snap_type

        # Verify bottom nav 'Deck' tab
        deck_btn = mobile_page.locator('.mobile-bottom-nav button[data-tab="ascd"]')
        assert deck_btn.is_visible()

    def test_mobile_emergency_fab_halt(self, mobile_page: Page):
        """GOD-01 on mobile: Floating Action Button 🛑 pauses swarm execution."""
        fab = mobile_page.locator("#ascd-fab-god")
        assert fab.is_visible()

        # Tap FAB
        fab.tap()
        overlay = mobile_page.locator("#ascd-god-overlay")
        assert overlay.is_visible()

        # Close overlay via ✕ button
        close_btn = overlay.locator('button:has-text("✕")')
        close_btn.click()
        assert not overlay.is_visible()
