import pytest
from fastapi.testclient import TestClient
from web.server import app

client = TestClient(app)

def test_smccc_ui_endpoint():
    response = client.get("/smccc")
    assert response.status_code == 200
    assert "Social Media Communication Command Center" in response.text
    assert "repair-btn" in response.text

def test_smccc_repair_endpoint():
    response = client.post("/api/smccc/repair")
    assert response.status_code == 200
    assert response.json() == {"karma": 15}

def test_smccc_campaign_endpoint():
    response = client.post("/api/smccc/campaign")
    assert response.status_code == 200
    assert response.json() == {"success": True}
