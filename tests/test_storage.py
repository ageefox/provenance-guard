import os

os.environ.setdefault("GROQ_API_KEY", "test-key")

import app as provenance_app


def test_json_storage_creates_its_parent_directory(tmp_path, monkeypatch):
    path = tmp_path / "state" / "audit.json"
    monkeypatch.setattr(provenance_app, "LOG_FILE", path)

    provenance_app.write_log([{"entry_type": "submission"}])

    assert path.exists()
    assert provenance_app.read_log() == [{"entry_type": "submission"}]
