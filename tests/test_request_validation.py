import os

import pytest

os.environ.setdefault("GROQ_API_KEY", "test-key")

import app as provenance_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(provenance_app, "CERT_FILE", str(tmp_path / "certificates.json"))
    monkeypatch.setattr(provenance_app, "LOG_FILE", str(tmp_path / "audit.json"))
    monkeypatch.setattr(provenance_app, "CONTENT_FILE", str(tmp_path / "content.json"))
    monkeypatch.setenv("ADMIN_API_KEY", "admin-key")
    provenance_app.app.config.update(TESTING=True)

    with provenance_app.app.test_client() as test_client:
        yield test_client


@pytest.mark.parametrize(
    ("endpoint", "payload", "field", "headers"),
    [
        ("/submit", {"text": 123, "creator_id": "writer"}, "text", {}),
        ("/submit", {"text": "sample", "creator_id": []}, "creator_id", {}),
        (
            "/appeal",
            {"content_id": {}, "creator_reasoning": "context"},
            "content_id",
            {},
        ),
        (
            "/appeal",
            {"content_id": "item", "creator_reasoning": 123},
            "creator_reasoning",
            {},
        ),
        ("/verify", {"creator_id": [], "statement": "mine"}, "creator_id", {}),
        ("/verify", {"creator_id": "writer", "statement": {}}, "statement", {}),
        (
            "/admin/approve_certificate",
            {"creator_id": 123},
            "creator_id",
            {"X-Admin-Key": "admin-key"},
        ),
    ],
)
def test_non_string_fields_are_rejected(client, endpoint, payload, field, headers):
    response = client.post(endpoint, json=payload, headers=headers)

    assert response.status_code == 400
    assert response.get_json() == {"error": f"Missing required field: {field}"}
