"""Smoke tests against a running container/pod.

Run after `docker compose up -d` or against a Minikube service:
    BASE_URL=http://localhost:5000 pytest -m smoke

Skipped automatically when BASE_URL is unset so unit-test runs aren't blocked.
"""
import os
import urllib.request
import json

import pytest

BASE_URL = os.environ.get("BASE_URL")

pytestmark = [
    pytest.mark.smoke,
    pytest.mark.skipif(not BASE_URL, reason="BASE_URL not set; skipping smoke tests"),
]


def _get(path):
    with urllib.request.urlopen(f"{BASE_URL}{path}", timeout=5) as r:
        return r.status, json.loads(r.read().decode("utf-8"))


def test_health_endpoint_live():
    status, body = _get("/health")
    assert status == 200
    assert body["status"] == "healthy"


def test_programs_endpoint_live():
    status, body = _get("/programs")
    assert status == 200
    assert "Fat Loss (FL)" in body


def test_status_endpoint_live():
    status, body = _get("/status")
    assert status == 200
    assert "capacity" in body
