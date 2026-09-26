"""Offline integrity and deterministic replay verification; never executes bundle content."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from vasp_app.reports import verify_bundle

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("bundle", type=Path)
parser.add_argument(
    "--trusted-fingerprint",
    help="Expected SHA-256 of the Ed25519 public key, obtained through a trusted channel",
)
args = parser.parse_args()
try:
    result = verify_bundle(args.bundle.read_bytes(), args.trusted_fingerprint)
    print(json.dumps(result, indent=2))
    if not result["identity_trusted"]:
        print("SIGNER IDENTITY NOT AUTHENTICATED: verify its fingerprint independently.", file=sys.stderr)
except Exception as exc:
    print("VERIFICATION FAILED: " + str(exc), file=sys.stderr)
    raise SystemExit(1)
