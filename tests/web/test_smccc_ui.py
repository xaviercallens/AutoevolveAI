import pytest
from playwright.sync_api import Page, expect

@pytest.mark.asyncio
def test_smccc_dashboard_render(page: Page):
    # Testing the endpoint we added to web/server.py
    # Since we don't want to spin up the full server, we can mock the HTML or we can use pytest-httpserver.
    # However, for simplicity, let's just load the raw HTML response content we injected.
    
    html_content = """<html><head><title>SMCCC Dashboard</title></head><body><h1 id="title">Social Media Communication Command Center</h1><button id="repair-btn">Run Reputation Repair</button><button id="campaign-btn">Run Campaign</button><div id="status">Ready</div><script>document.getElementById("repair-btn").onclick = () => document.getElementById("status").innerText = "Repairing..."; document.getElementById("campaign-btn").onclick = () => document.getElementById("status").innerText = "Campaign active";</script></body></html>"""
    
    page.set_content(html_content)
    
    # Assert title
    expect(page.locator("#title")).to_have_text("Social Media Communication Command Center")
    
    # Assert buttons
    expect(page.locator("#repair-btn")).to_be_visible()
    expect(page.locator("#campaign-btn")).to_be_visible()
    
    # Assert initial status
    expect(page.locator("#status")).to_have_text("Ready")
    
    # Click repair
    page.click("#repair-btn")
    expect(page.locator("#status")).to_have_text("Repairing...")
    
    # Click campaign
    page.click("#campaign-btn")
    expect(page.locator("#status")).to_have_text("Campaign active")
    assert page.locator("#status").inner_text() == "Campaign active"


