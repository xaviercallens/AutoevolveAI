import pytest
import multiprocessing
import uvicorn
import time
import requests
import os
from playwright.sync_api import Page, expect
from web.server import app

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8003, log_level="error")

@pytest.fixture(scope="session", autouse=True)
def start_server():
    proc = multiprocessing.Process(target=run_server, daemon=True)
    proc.start()
    for _ in range(60):
        try:
            if requests.get("http://127.0.0.1:8003/health").status_code == 200:
                break
        except requests.ConnectionError:
            pass
        time.sleep(0.5)
    yield
    proc.terminate()
    proc.join()

def test_smccc_e2e_and_screenshot(page: Page):
    os.makedirs("docs/images", exist_ok=True)
    
    # 1. Boot up UI
    page.goto("http://127.0.0.1:8003/")
    
    # Wait for tabs to render
    page.wait_for_selector("button[onclick=\"switchTab('smccc')\"]")
    
    # Take screenshot of main dashboard
    page.screenshot(path="docs/images/main_dashboard.png")
    
    # 2. Navigate to SMCCC
    page.locator("button[onclick=\"switchTab('smccc')\"]").first.click()
    page.wait_for_selector("#section-smccc:not(.hidden)")
    
    # Take screenshot of SMCCC empty state
    page.screenshot(path="docs/images/smccc_dashboard_ready.png")
    
    # 3. Trigger Reputation Repair
    page.click("#btn-smccc-repair")
    expect(page.locator("#smccc-output")).to_contain_text("Karma acquired: 15", timeout=10000)
    
    # Take screenshot of Success State
    page.screenshot(path="docs/images/smccc_dashboard_success.png")
    
    # 4. Trigger Campaign
    page.click("#btn-smccc-campaign")
    expect(page.locator("#smccc-output")).to_contain_text("Broadcast success: true", timeout=10000)
    
    # Final Screenshot
    page.screenshot(path="docs/images/smccc_dashboard_final.png")
