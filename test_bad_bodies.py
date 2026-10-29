#!/usr/bin/env python3
"""
Regression test: a request body that isn't a JSON object must not crash /submit.

    python test_bad_bodies.py

The bug: reading `payload.get("text")` straight after `request.get_json()`
crashes with a 500 when the body isn't a JSON object. A plain-text body gives
`None`, a JSON list gives a `list`, and neither has `.get`. The crash also
left nothing in the audit log. The fix is the `isinstance(payload, dict)`
guard at the top of Step 2 in `app.py::submit`.

Runs against a throwaway audit log and never loads the model.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["AI201_AUDIT_LOG"] = os.path.join(tempfile.mkdtemp(), "audit.jsonl")

import app    # noqa: E402
import audit  # noqa: E402

CASES = [
    ("plain-text body", dict(data="hello", headers={"Content-Type": "text/plain"})),
    ("JSON list", dict(json=["x"])),
    ("JSON string", dict(json="just a string")),
    ("JSON number", dict(json=42)),
    ("JSON null", dict(data="null", headers={"Content-Type": "application/json"})),
    ("broken JSON", dict(data="{not json", headers={"Content-Type": "application/json"})),
]


def main():
    app.app.config["PROPAGATE_EXCEPTIONS"] = False   # a crash shows as a 500, as a client sees it
    client = app.app.test_client()
    failures = 0
    for name, request_kwargs in CASES:
        before = len(audit.read_entries())
        response = client.post("/submit", **request_kwargs)
        body = response.get_json(silent=True) or {}
        logged = [e for e in audit.read_entries()[before:] if e.get("event") == "rejected"]
        ok = response.status_code == 400 and "error" in body and len(logged) == 1
        failures += not ok
        print(f"[{'PASS' if ok else 'FAIL'}] {name:16} -> {response.status_code} "
              f"{body.get('error')}, rejections logged: {len(logged)}")
    print(f"\n{len(CASES) - failures} of {len(CASES)} passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
