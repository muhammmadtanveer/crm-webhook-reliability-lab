# CRM Webhook Reliability Lab

A dependency-free Python reference implementation for safely receiving CRM and marketing-automation webhooks.

## Why this matters

A lead workflow can silently break when duplicate events create duplicate opportunities, malformed payloads bypass validation, or unauthenticated requests reach internal systems. This project models the reliability controls that turn webhook automation into dependable IT infrastructure.

## Capabilities

- HMAC SHA-256 signature verification
- Strict event-schema validation
- Idempotency journal backed by JSON storage
- Deterministic routing for high-intent, nurture, and data-quality-review queues
- JSON audit output suitable for an API gateway, CRM adapter, or incident log

## Run it

```bash
python3 app.py fixtures/events.json
```

Run it twice: the first pass accepts unique events; the second pass marks them as duplicates. This demonstrates idempotent processing.

## Architecture

```text
Webhook request → signature verification → schema validation → idempotency check
                                                           → lead routing → audit result
```

## Production considerations

The fixture uses a demonstrative secret only. Production deployments should retrieve secrets from a managed secret store, persist idempotency keys in a transactional database with TTLs, add retry/dead-letter handling, and use authenticated transport with access controls.
