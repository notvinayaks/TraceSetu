"""Run an explicit public-data validation plan. Passwords come from the environment or a local bootstrap file."""
import argparse
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from vasp_app.live_validation import ValidationPlan, run_check  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("--base-url", default="http://127.0.0.1:8787")
    parser.add_argument("--username", default="investigator")
    parser.add_argument("--bootstrap-file", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--trusted-fingerprint")
    args = parser.parse_args()
    url = urlsplit(args.base_url)
    local = url.hostname in ("localhost", "127.0.0.1", "::1")
    if url.username or url.password or url.query or url.fragment or url.path not in ("", "/"):
        parser.error("Base URL must contain only scheme, host and optional port")
    if url.scheme != "https" and not (url.scheme == "http" and local):
        parser.error("Remote installations require HTTPS")
    plan = ValidationPlan.model_validate_json(args.plan.read_bytes())
    password = os.environ.get("ATLAS_VALIDATION_PASSWORD", "")
    if args.bootstrap_file:
        if not local:
            parser.error("Bootstrap-file login is only permitted for a loopback installation")
        match = re.search(r"^" + re.escape(args.username) + r": (.+)$", args.bootstrap_file.read_text(), re.M)
        if not match:
            parser.error("Account is absent from bootstrap file")
        password = match[1].strip()
    if not password:
        parser.error("Set ATLAS_VALIDATION_PASSWORD or use a private local --bootstrap-file")
    args.output.mkdir(parents=True, exist_ok=False)
    manifests = []
    with httpx.Client(base_url=args.base_url.rstrip("/"), timeout=30, follow_redirects=False) as client:
        response = client.post("/api/auth/login", json={"username": args.username, "password": password})
        response.raise_for_status()
        client.headers["X-CSRF-Token"] = response.json()["csrf"]
        password = None
        for check in plan.checks:
            try:
                result = run_check(client, check, args.output, trusted_fingerprint=args.trusted_fingerprint)
            except Exception as exc:
                result = {"check": check.name, "chain": check.spec.chain, "status": "failed",
                    "error_type": type(exc).__name__, "full_chain_validated": False, "ownership_validated": False}
            manifests.append(result)
            print(json.dumps({"chain": check.spec.chain, "check": check.name, "status": result["status"]}), flush=True)
        client.post("/api/auth/logout")
    summary = {"schema": "tracesetu.live-validation.v1", "checks": manifests,
        "scope": "Bounded acquisition, reference matching and evidence replay; not independent attribution certification"}
    (args.output / "manifest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return 0 if all(row["status"] == "bounded_transfer_sample_verified" for row in manifests) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status": "failed", "error_type": type(exc).__name__}), file=sys.stderr)
        raise SystemExit(1)
