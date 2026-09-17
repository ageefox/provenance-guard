# Provenance Guard

Provenance Guard is a course prototype for exploring transparent authorship labels. It combines an LLM assessment with two simple writing-style heuristics, records the individual scores, and gives creators a path to appeal a result.

The project demonstrates API design, ensemble scoring, audit logging, rate limiting, and a small certificate workflow. It is not a validated AI-text detector and should not be used to make academic, employment, moderation, or disciplinary decisions.

## How it works

`POST /submit` evaluates text using three signals:

- an LLM classification from Groq
- sentence structure and vocabulary statistics
- word-repetition burstiness

The API returns each signal, a weighted score, and one of three deliberately cautious labels: `likely_human`, `uncertain`, or `likely_ai`. Text shorter than 50 words cannot receive a high-confidence AI label.

Creators can appeal a classification through `POST /appeal`. The certificate flow uses `POST /verify` to create a pending request and a protected admin endpoint to approve it.

## Run locally

Requires Python 3.10 or newer and a [Groq API key](https://console.groq.com/keys).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `GROQ_API_KEY` and a private `ADMIN_API_KEY` in `.env`, then start the API:

```bash
python app.py
```

The service runs at `http://localhost:5001`. Check it with:

```bash
curl http://localhost:5001/health
```

Runtime records are written under `.data/`, which is ignored by Git. Set `PROVENANCE_DATA_DIR` to use another local directory.

## API

- `POST /submit` — analyze text and return the component scores
- `POST /appeal` — mark a stored classification for human review
- `POST /verify` — request a creator certificate
- `POST /admin/approve_certificate` — approve a request using the `X-Admin-Key` header
- `GET /log` — return the 50 most recent audit entries to an administrator
- `GET /dashboard` — return aggregate submission and appeal statistics to an administrator
- `GET /health` — report service health

Certificate approval, the audit log, and dashboard require the `X-Admin-Key` header. The scoring flow and storage design are documented in [`docs/architecture.md`](docs/architecture.md).

## Tests

Install the development dependencies and run the suite:

```bash
pip install -r requirements-dev.txt
pytest -q
```

The tests use temporary JSON stores and do not call the Groq API.

## Limitations

- The scoring thresholds and heuristic weights have not been calibrated on a representative dataset.
- Writing style is not reliable proof of authorship; formal writing and writing by non-native English speakers may be misclassified.
- The certificate process records manual approval. It does not cryptographically establish a person's identity or how a document was created.
- A shared admin key is suitable only for this prototype. A deployed service would need user authentication, authorization, secret management, and key rotation.
- JSON files are used for local persistence and do not support concurrent production workloads.
- Appeals use possession of a content ID and do not authenticate the original creator.
