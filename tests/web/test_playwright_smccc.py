import pytest
import multiprocessing
import uvicorn
import time
import requests
from playwright.sync_api import Page, expect
from web.server import app

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="warning")

@pytest.fixture(scope="session", autouse=True)
def start_server():
    proc = multiprocessing.Process(target=run_server, daemon=True)
    proc.start()
    
    # Wait for server to boot
    for _ in range(30):
        try:
            r = requests.get("http://127.0.0.1:8001/health")
            if r.status_code == 200:
                break
        except requests.ConnectionError:
            pass
        time.sleep(0.1)
        
    yield
    proc.terminate()
    proc.join()

def test_smccc_functional_flow(page: Page):
    page.goto("http://127.0.0.1:8001/smccc")
    
    # Verify elements
    expect(page.locator("#title")).to_have_text("Social Media Communication Command Center")
    expect(page.locator("#status")).to_have_text("Ready")
    
    # Test Repair Flow
    page.click("#repair-btn")
    expect(page.locator("#status")).to_have_text("Karma: 15", timeout=10000)
    
    # Test Campaign Flow
    page.click("#campaign-btn")
    expect(page.locator("#status")).to_have_text("Success: true", timeout=10000)
    assert page.locator("#status").inner_text() == "Success: true"

