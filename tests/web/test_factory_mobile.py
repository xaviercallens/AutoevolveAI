"""
test_factory_mobile.py — Tests for PWA manifest, service worker, and mobile-responsive HTML.

Verifies that the web server correctly serves manifest.json, sw.js,
and that the HTML includes the necessary PWA and responsive tags.
"""

from __future__ import annotations

import json
import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _factory_db_tmp(tmp_path, monkeypatch):
    """Use a temporary SQLite database for each test."""
    db_path = tmp_path / "test_missions.db"
    monkeypatch.setenv("FACTORY_DB_PATH", str(db_path))
    from web import factory
    factory.DB_PATH = db_path


@pytest.fixture
def client():
    from web.server import app
    return TestClient(app)


class TestManifest:
    def test_manifest_served(self, client):
        resp = client.get("/manifest.json")
        assert resp.status_code == 200
        assert "application/manifest+json" in resp.headers.get("content-type", "")

    def test_manifest_valid_json(self, client):
        resp = client.get("/manifest.json")
        data = resp.json()
        assert data["name"] == "SuperGravity PR Factory"
        assert data["short_name"] == "SG Factory"
        assert data["display"] == "standalone"
        assert data["theme_color"] == "#10b981"

    def test_manifest_has_icons(self, client):
        resp = client.get("/manifest.json")
        data = resp.json()
        assert len(data["icons"]) >= 2
        sizes = [icon["sizes"] for icon in data["icons"]]
        assert "192x192" in sizes
        assert "512x512" in sizes


class TestServiceWorker:
    def test_sw_served(self, client):
        resp = client.get("/sw.js")
        assert resp.status_code == 200
        assert "javascript" in resp.headers.get("content-type", "")

    def test_sw_has_worker_allowed_header(self, client):
        resp = client.get("/sw.js")
        assert resp.headers.get("Service-Worker-Allowed") == "/"

    def test_sw_contains_cache_strategy(self, client):
        resp = client.get("/sw.js")
        content = resp.text
        assert "CACHE_NAME" in content
        assert "install" in content
        assert "fetch" in content


class TestIcons:
    def test_icon_192_served(self, client):
        resp = client.get("/icons/icon-192.png")
        assert resp.status_code == 200

    def test_icon_512_served(self, client):
        resp = client.get("/icons/icon-512.png")
        assert resp.status_code == 200

    def test_icon_404_nonexistent(self, client):
        resp = client.get("/icons/nonexistent.png")
        assert resp.status_code == 404


class TestHTMLPWATags:
    def test_index_has_viewport_meta(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.text
        assert 'viewport-fit=cover' in html

    def test_index_has_manifest_link(self, client):
        resp = client.get("/")
        html = resp.text
        assert 'rel="manifest"' in html
        assert '/manifest.json' in html

    def test_index_has_theme_color(self, client):
        resp = client.get("/")
        html = resp.text
        assert 'name="theme-color"' in html

    def test_index_has_apple_meta_tags(self, client):
        resp = client.get("/")
        html = resp.text
        assert 'apple-mobile-web-app-capable' in html
        assert 'apple-touch-icon' in html

    def test_index_has_factory_tab(self, client):
        resp = client.get("/")
        html = resp.text
        assert "tab-factory" in html
        assert "section-factory" in html

    def test_index_has_mobile_bottom_nav(self, client):
        resp = client.get("/")
        html = resp.text
        assert "mobile-bottom-nav" in html

    def test_index_has_sw_registration(self, client):
        resp = client.get("/")
        html = resp.text
        assert "serviceWorker" in html
        assert "sw.js" in html
