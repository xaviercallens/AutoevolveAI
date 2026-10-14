import pytest
import multiprocessing
import uvicorn
import time
import requests
from playwright.sync_api import Page, expect
from web.server import app

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="warning")

@pytest.fixture(scope="session", autouse=True)
def start_server():
    proc = multiprocessing.Process(target=run_server, daemon=True)
    proc.start()
    
    # Wait for server to boot
    for _ in range(60):
        try:
            r = requests.get("http://127.0.0.1:8002/health")
            if r.status_code == 200:
                break
        except requests.ConnectionError:
            pass
        time.sleep(0.5)
        
    yield
    proc.terminate()
    proc.join()

def test_full_dashboard_navigation(page: Page):
    page.goto("http://127.0.0.1:8002/")
    
    # Verify Title
    expect(page).to_have_title("AutoevolveAI & SuperGravity — Interactive ANSE Explorer")
    
    # List of tabs to verify
    tabs = [
        "concepts", "phase1", "phase2", "autopoiesis", "phase3",
        "symbiotic", "evolution", "factory", "ascd", "anse-v2",
        "anse-v3", "anse-v4", "anse-v5", "scenario-studio", "smccc"
    ]
    
    for tab in tabs:
        # Click the tab button
        tab_btn = page.locator(f"button[onclick=\"switchTab('{tab}')\"]").first
        tab_btn.click()
        
        # Verify the section becomes visible
        section = page.locator(f"#section-{tab}")
        expect(section).not_to_have_class("hidden")
        
        # For SMCCC, check specific content
        if tab == "smccc":
            expect(section.locator("h2")).to_contain_text("Social Media Communication Command Center")
            expect(section.locator("#btn-smccc-repair")).to_be_visible()
            expect(section.locator("#btn-smccc-campaign")).to_be_visible()

def test_smccc_repair_functional(page: Page):
    page.goto("http://127.0.0.1:8002/")
    page.locator("button[onclick=\"switchTab('smccc')\"]").first.click()
    page.click("#btn-smccc-repair")
    expect(page.locator("#smccc-output")).to_contain_text("Karma acquired: 15", timeout=10000)

def test_smccc_campaign_functional(page: Page):
    page.goto("http://127.0.0.1:8002/")
    page.locator("button[onclick=\"switchTab('smccc')\"]").first.click()
    page.click("#btn-smccc-campaign")
    expect(page.locator("#smccc-output")).to_contain_text("Broadcast success: true", timeout=10000)
