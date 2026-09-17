import json
import os

import pytest

os.environ.setdefault("GROQ_API_KEY", "test-key")

import app as provenance_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(provenance_app, "CERT_FILE", str(tmp_path / "certificates.json"))
    monkeypatch.setattr(provenance_app, "LOG_FILE", str(tmp_path / "audit.json"))
    monkeypatch.delenv("ADMIN_API_KEY", raising=False)
    provenance_app.app.config.update(TESTING=True)

    with provenance_app.app.test_client() as test_client:
        yield test_client


def test_approval_is_disabled_without_an_admin_key(client):
    response = client.post("/admin/approve_certificate", json={"creator_id": "writer-1"})

    assert response.status_code == 503
    assert response.get_json() == {"error": "Admin access is not configured"}


def test_approval_rejects_an_invalid_admin_key(client, monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "correct-key")

    response = client.post(
        "/admin/approve_certificate",
        headers={"X-Admin-Key": "wrong-key"},
        json={"creator_id": "writer-1"},
    )

    assert response.status_code == 401
    assert response.get_json() == {"error": "Unauthorized"}


def test_authorized_admin_can_approve_a_pending_certificate(client, monkeypatch, tmp_path):
    monkeypatch.setenv("ADMIN_API_KEY", "correct-key")
    request_response = client.post(
        "/verify",
        json={"creator_id": "writer-1", "statement": "I wrote this work."},
    )

    response = client.post(
        "/admin/approve_certificate",
        headers={"X-Admin-Key": "correct-key"},
        json={"creator_id": "writer-1"},
    )

    assert request_response.status_code == 200
    assert response.status_code == 200
    assert response.get_json()["status"] == "verified"

    certificates = json.loads((tmp_path / "certificates.json").read_text())
    assert certificates["writer-1"]["status"] == "verified"

    audit_entries = json.loads((tmp_path / "audit.json").read_text())
    assert audit_entries[-1]["entry_type"] == "certificate_issued"
    assert audit_entries[-1]["creator_id"] == "writer-1"


def test_authorized_admin_cannot_approve_an_unknown_creator(client, monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "correct-key")

    response = client.post(
        "/admin/approve_certificate",
        headers={"X-Admin-Key": "correct-key"},
        json={"creator_id": "missing"},
    )

    assert response.status_code == 404


@pytest.mark.parametrize("endpoint", ["/log", "/dashboard"])
def test_operational_endpoints_are_disabled_without_an_admin_key(client, endpoint):
    response = client.get(endpoint)

    assert response.status_code == 503
    assert response.get_json() == {"error": "Admin access is not configured"}


@pytest.mark.parametrize("endpoint", ["/log", "/dashboard"])
def test_operational_endpoints_reject_an_invalid_admin_key(client, monkeypatch, endpoint):
    monkeypatch.setenv("ADMIN_API_KEY", "correct-key")

    response = client.get(endpoint, headers={"X-Admin-Key": "wrong-key"})

    assert response.status_code == 401
    assert response.get_json() == {"error": "Unauthorized"}


@pytest.mark.parametrize("endpoint", ["/log", "/dashboard"])
def test_authorized_admin_can_read_operational_endpoints(client, monkeypatch, endpoint):
    monkeypatch.setenv("ADMIN_API_KEY", "correct-key")

    response = client.get(endpoint, headers={"X-Admin-Key": "correct-key"})

    assert response.status_code == 200
