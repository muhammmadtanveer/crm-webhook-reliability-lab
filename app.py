"""CRM Webhook Reliability Lab."""
import argparse, hashlib, hmac, json
from dataclasses import dataclass
from pathlib import Path

REQUIRED = {"event_id", "event_type", "lead"}
DEMO_SECRET = b"replace-this-demo-secret"

@dataclass
class Audit:
    event_id: str
    status: str
    route: str | None = None
    reason: str | None = None

class IdempotencyJournal:
    def __init__(self, path="processed_events.json"):
        self.path = Path(path)
        self.keys = set(json.loads(self.path.read_text())) if self.path.exists() else set()
    def seen(self, key): return key in self.keys
    def record(self, key):
        self.keys.add(key)
        self.path.write_text(json.dumps(sorted(self.keys), indent=2))

def verify_signature(body, signature, secret=DEMO_SECRET):
    expected = hmac.new(secret, body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

def validate(event):
    missing = REQUIRED - set(event)
    if missing: raise ValueError("Missing fields: " + ", ".join(sorted(missing)))
    lead = event["lead"]
    if not isinstance(lead, dict) or not lead.get("email"):
        raise ValueError("lead.email is required")
    if event["event_type"] not in {"lead.created", "lead.updated"}:
        raise ValueError("Unsupported event type")

def route(event):
    lead = event["lead"]
    if lead.get("consent") is not True: return "data-quality-review"
    score = int(lead.get("score", 0))
    if score >= 80: return "high-intent-sales"
    return "nurture-automation"

def process(event, journal):
    validate(event)
    if journal.seen(event["event_id"]):
        return Audit(event["event_id"], "duplicate", reason="idempotency key already processed")
    journal.record(event["event_id"])
    return Audit(event["event_id"], "accepted", route=route(event))

def main():
    parser = argparse.ArgumentParser(description="Process validated CRM webhook fixtures.")
    parser.add_argument("fixture")
    parser.add_argument("--journal", default="processed_events.json")
    args = parser.parse_args()
    payload = json.loads(Path(args.fixture).read_text())
    journal = IdempotencyJournal(args.journal)
    results = []
    for event in payload:
        try: results.append(Audit(**process(event, journal).__dict__).__dict__)
        except ValueError as error: results.append(Audit(event.get("event_id", "unknown"), "rejected", reason=str(error)).__dict__)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
