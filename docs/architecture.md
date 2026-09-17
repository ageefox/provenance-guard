# Application design

Provenance Guard is a single-process Flask prototype. It combines one remote classification result with two local writing-style measurements, records the component scores, and supports appeals and manually approved creator certificates.

## Submission flow

`POST /submit` performs these steps:

1. Validate the text and creator ID.
2. Check whether the creator has an approved certificate.
3. Request an authorship score from the configured Groq model.
4. Calculate the local stylometric and word-repetition scores.
5. Combine the three scores and assign an attribution band.
6. Write an audit entry and a smaller content record.

The combined score uses fixed weights: 50% remote classifier, 30% stylometric score, and 20% word-repetition score. Scores below `0.40` map to `likely_human`; scores from `0.40` through `0.6999` map to `uncertain`; and scores of `0.70` or more map to `likely_ai`.

Texts shorter than 50 words cannot receive a `likely_ai` result. Their combined score is capped at `0.69` when necessary because the two local measurements have little evidence at that length.

If the remote classifier is unavailable or returns an invalid response, its component score falls back to `0.50` and the request still completes.

## Appeals and certificates

`POST /appeal` accepts a content ID and an explanation. It marks the stored content as `under_review` and adds an appeal entry to the audit log. The prototype does not authenticate the person submitting an appeal.

`POST /verify` creates a pending certificate request. An administrator can approve an existing request through `POST /admin/approve_certificate`. Approved creator IDs receive a different label on later submissions.

Certificate approval, the audit log, and dashboard statistics require the `X-Admin-Key` header. If `ADMIN_API_KEY` is not configured, these operations remain disabled.

## Local storage

The application keeps three JSON files under `.data/`:

- `audit_log.json` contains submission, appeal, and certificate events.
- `content_store.json` contains the current status and score for each content ID.
- `certificate_store.json` contains pending and approved certificate requests.

Set `PROVENANCE_DATA_DIR` to use another directory. The files under [`examples/`](../examples/) illustrate the record format and are not loaded by the application.

JSON storage keeps the prototype easy to inspect, but it is not safe for concurrent production writes. The rate limiter also uses in-memory state. A deployed service would need transactional storage, durable rate-limit state, user authentication, and managed secrets.

## Scope

The score weights and thresholds are hand-set and have not been calibrated against a representative evaluation dataset. The output is a demonstration of transparent scoring and review workflows, not proof of how a document was authored.
