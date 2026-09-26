"""Portable, signed evidence; signatures establish integrity, not the truth of assertions."""

from __future__ import annotations
import csv
import hashlib
import io
import json
import threading
import zipfile
from datetime import datetime, timezone
from xml.sax.saxutils import escape
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from .store import canonical, read_artifact
from .config import settings

_key_lock = threading.Lock()


def signing_key():
    path = settings.data_dir / "evidence-signing.key"
    with _key_lock:
        if not path.exists():
            key = Ed25519PrivateKey.generate()
            try:
                with path.open("xb") as f:
                    f.write(
                        key.private_bytes(
                            serialization.Encoding.Raw,
                            serialization.PrivateFormat.Raw,
                            serialization.NoEncryption(),
                        )
                    )
            except FileExistsError:
                pass
        return Ed25519PrivateKey.from_private_bytes(path.read_bytes())


def pdf_report(case, job, analysis):
    out = io.BytesIO()
    styles = getSampleStyleSheet()
    for name in ("Heading1", "Heading2", "Heading3"):
        styles[name].keepWithNext = True
    styles.add(
        ParagraphStyle(
            name="AtlasTitle",
            fontName="Helvetica-Bold",
            fontSize=26,
            leading=30,
            textColor=colors.HexColor("#142D3B"),
            spaceAfter=15,
        )
    )
    styles.add(ParagraphStyle(name="AtlasBody", fontSize=9, leading=13, spaceAfter=8, wordWrap="CJK"))
    styles.add(ParagraphStyle(name="AtlasSmall", fontSize=7, leading=10, wordWrap="CJK"))

    def p(text, style="AtlasBody"):
        return Paragraph(escape(str(text)), styles[style])

    story = [
        p("TRACESETU", "Heading2"),
        p("Investigation intelligence report", "AtlasTitle"),
        p(f"{case['reference']} | {case['title']}"),
        p(
            "SYNTHETIC TRAINING DATA - NOT REAL EVIDENCE"
            if analysis["mode"] == "fixture"
            else f"Evidence mode: {analysis['mode'].upper()}"
        ),
        p(f"Analysis: {job.id}"),
        p("Generated UTC: " + datetime.now(timezone.utc).isoformat()),
        p(
            "This report supports investigator review. It does not identify a beneficial owner, establish guilt, or show that funds have been frozen."
        ),
        Spacer(1, 10),
    ]
    cert = analysis["certificate"]
    spec = cert["specification"]
    nearest = (
        f"{cert['nearest_evidenced_hops']} hops"
        if cert["nearest_evidenced_hops"] is not None
        else "not established"
    )
    story += [
        p("Scope and outcome", "Heading2"),
        p(f"Chain: {spec['chain']} | Address: {spec['address']}"),
        p(
            f"Window: {datetime.fromtimestamp(spec['start'], timezone.utc).isoformat()} to {datetime.fromtimestamp(spec['end'], timezone.utc).isoformat()} | Maximum hops: {spec['max_hops']}"
        ),
        p(
            f"Nearest evidenced custody: {nearest}. Nearest known target proven within the bounded snapshot: {cert['nearest_known_target_in_snapshot_proven']}. Nearest real VASP proven: {cert['nearest_real_vasp_proven']}."
        ),
        p(cert["identity_coverage"]),
        p(cert["scope"]),
    ]
    execution = job.result.get("execution") if job.result else None
    if execution:
        story += [
            p("Selected query execution", "Heading2"),
            p(
                "Synthetic training expansion; no provider calls."
                if execution["mode"] == "fixture"
                else "Selected scopes acquired under a durable per-job request budget."
            ),
            p(
                f"Reserved request slots: {execution['reserved_request_slots']} / {execution['budget_requests']}; preserved HTTP responses: {execution['successful_http_responses']}; cache hits: {execution['cache_hits']}. Slots survive recovery and may include an undispatched attempt."
            ),
            p("Preserved parent snapshot SHA-256: " + execution["parent_snapshot_sha256"], "AtlasSmall"),
            p("Executed plan SHA-256: " + execution["plan_sha256"], "AtlasSmall"),
        ]
        for scope in execution["actions"]:
            story.append(
                p(
                    f"{scope['chain']}:{scope['address']} | {scope['status']} | {scope.get('reason', 'New service boundary; skipped')}",
                    "AtlasSmall",
                )
            )
    story.append(p("Custody candidates and supporting assertions", "Heading2"))
    if not analysis["candidates"]:
        story.append(p("No supported custody candidate was found. This is not a low-risk determination."))
    for i, c in enumerate(analysis["candidates"]):
        story += [
            p(f"{i + 1}. {c['entity']} - {c['hops']} hops / {c['status']}", "Heading3"),
            p(f"{c['chain']}:{c['address']} | Deposit role: {c['deposit_role']}"),
            p("Path event IDs: " + ", ".join(c["path"])),
            p(
                "Possible exposure upper bound (asset base units): "
                + str(c["amount_bounds"]["upper"])
                + "; lower bound: 0. "
                + c["amount_bounds"]["meaning"]
            ),
        ]
        for a in c["assertions"]:
            story.append(
                p(
                    f"Assertion {a['id']} | {a['grade']} | {a['source_family']} | {a['source']} | Evidence: {', '.join(a['evidence'])}"
                )
            )
    story.append(p("Unresolved frontiers", "Heading2"))
    if not any(f["reason"] != "custody_boundary" for f in analysis["frontiers"]):
        story.append(
            p(
                "None within the declared snapshot and traversal bounds. Real-world identity and provider coverage are separate limits."
            )
        )
    for f in analysis["frontiers"]:
        if f["reason"] != "custody_boundary":
            story.append(
                p(f"{f['chain']}:{f['address']} at {f['hops']} hops: {f['reason']}. {f.get('detail', '')}")
            )
    story.append(p("Observed transfer register", "Heading2"))
    for e in analysis["graph"]["events"]:
        story.append(
            p(
                f"{e['id']} | {', '.join(e['senders'])} -> {e['recipient']} | {e['amount']} base units ({e['decimals']} decimals) | {e['asset']} | {e['finality']} | Evidence {', '.join(e['evidence'])}",
                "AtlasSmall",
            )
        )
        if e.get("bridge_details"):
            b = e["bridge_details"]
            story += [
                p(
                    f"CCTP V2 delivery: {e['chain']} to {e['destination_chain']} | Registry {b['registry_version']} | {b['grade']}",
                    "AtlasSmall",
                ),
                p(
                    f"Burned {b['burned_amount']}; fee {b['fee_amount']}; minted {b['minted_amount']} USDC base units (6 decimals). Destination transaction: {b['destination_txhash']}",
                    "AtlasSmall",
                ),
                p(
                    f"Destination mint UTC: {datetime.fromtimestamp(b['destination_timestamp'], timezone.utc).isoformat()} | Position {b['destination_position']} | Nonce: {b['nonce']}",
                    "AtlasSmall",
                ),
                p(
                    "Attestation signers: "
                    + ", ".join(b["attestation_signers"])
                    + " | Source family: "
                    + b["source_family"],
                    "AtlasSmall",
                ),
                p(b["trust"], "AtlasSmall"),
            ]
    story.append(p("Interpretation limits and integrity", "Heading2"))
    for text in analysis["limitations"]:
        story.append(p(text))
    story += [
        p("Snapshot SHA-256: " + cert["snapshot_sha256"], "AtlasSmall"),
        p(
            "Engine: "
            + cert["engine_version"]
            + " | The signed ZIP manifest binds the files. Validate the signer fingerprint through a trusted channel. A valid signature alone does not authenticate an agency or verify provider claims."
        ),
    ]

    def footer(canvas, doc):
        canvas.setStrokeColor(colors.HexColor("#D7E3E8"))
        canvas.line(42, 43, 553, 43)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(42, 30, "RESTRICTED | TraceSetu | " + analysis["mode"].upper())
        canvas.drawRightString(553, 30, f"{doc.page}")

    SimpleDocTemplate(
        out,
        pagesize=(595, 842),
        leftMargin=42,
        rightMargin=42,
        topMargin=42,
        bottomMargin=58,
        title="TraceSetu investigation report",
    ).build(story, onFirstPage=footer, onLaterPages=footer)
    return out.getvalue()


def make_bundle(case, job, audits):
    analysis = job.result["analysis"]
    files = {
        "snapshot.json": read_artifact(job.result["snapshot_sha256"]),
        "analysis.json": canonical(analysis),
        "case.json": canonical(case),
        "audit.json": canonical(audits),
        "report.pdf": pdf_report(case, job, analysis),
    }
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(
        [
            "event_id",
            "chain",
            "txid",
            "senders",
            "recipient",
            "asset",
            "amount_base_units",
            "decimals",
            "timestamp",
            "finality",
            "evidence",
            "kind",
            "destination_chain",
            "destination_asset",
            "bridge_proof",
            "destination_txid",
            "destination_timestamp",
            "burned_amount_base_units",
            "fee_amount_base_units",
            "minted_amount_base_units",
        ]
    )

    def safe(v):
        s = str(v)
        return "'" + s if s.startswith(("=", "+", "-", "@", "\t", "\r")) else s

    for e in analysis["graph"]["events"]:
        writer.writerow(
            [
                safe(v)
                for v in [
                    e["id"],
                    e["chain"],
                    e["txid"],
                    ";".join(e["senders"]),
                    e["recipient"],
                    e["asset"],
                    e["amount"],
                    e["decimals"],
                    e["timestamp"],
                    e["finality"],
                    ";".join(e["evidence"]),
                    e["kind"],
                    e.get("destination_chain") or "",
                    e.get("destination_asset") or "",
                    e.get("bridge_proof") or "",
                    e.get("bridge_details", {}).get("destination_txhash", ""),
                    e.get("bridge_details", {}).get("destination_timestamp", ""),
                    e.get("bridge_details", {}).get("burned_amount", ""),
                    e.get("bridge_details", {}).get("fee_amount", ""),
                    e.get("bridge_details", {}).get("minted_amount", ""),
                ]
            ]
        )
    files["transfers.csv"] = stream.getvalue().encode("utf-8-sig")
    for raw in job.result.get("raw_evidence", []):
        files["raw/" + raw["sha256"] + ".json"] = read_artifact(raw["sha256"])
    files["acquisition.json"] = canonical(job.result.get("raw_evidence", []))
    if job.result.get("acquisition_metrics_sha256"):
        files["acquisition-metrics.json"] = read_artifact(job.result["acquisition_metrics_sha256"])
    manifest = {
        "schema": "atlas.evidence.v1",
        "job_id": job.id,
        "mode": analysis["mode"],
        "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())},
        "limitations": [
            "Local signing key; agency identity must be verified out of band.",
            "Audit export is not a tamper-proof external audit service.",
        ],
    }
    key = signing_key()
    public = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    files["manifest.json"] = canonical(manifest)
    files["manifest.sig"] = key.sign(files["manifest.json"])
    files["signer.pub"] = public
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            z.writestr(name, data)
    return out.getvalue(), hashlib.sha256(public).hexdigest()


def verify_bundle(data, trusted_fingerprint=None):
    if len(data) > 100_000_000:
        raise ValueError("Bundle exceeds size limit")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        infos = z.infolist()
        names = [i.filename for i in infos]
        if len(names) != len(set(names)) or len(names) > 2000:
            raise ValueError("Duplicate or excessive bundle members")
        if sum(i.file_size for i in infos) > 200_000_000:
            raise ValueError("Expanded bundle exceeds size limit")
        if any(".." in name.split("/") or name.startswith(("/", "\\")) or "\\" in name for name in names):
            raise ValueError("Unsafe bundle path")
        public = z.read("signer.pub")
        manifest_bytes = z.read("manifest.json")
        Ed25519PublicKey.from_public_bytes(public).verify(z.read("manifest.sig"), manifest_bytes)
        manifest = json.loads(manifest_bytes)
        if manifest.get("schema") != "atlas.evidence.v1":
            raise ValueError("Unknown bundle schema")
        if set(names) != set(manifest["files"]) | {"manifest.json", "manifest.sig", "signer.pub"}:
            raise ValueError("Manifest membership mismatch")
        for name, h in manifest["files"].items():
            if hashlib.sha256(z.read(name)).hexdigest() != h:
                raise ValueError(f"Hash mismatch: {name}")
        fp = hashlib.sha256(public).hexdigest()
        if trusted_fingerprint and fp != trusted_fingerprint:
            raise ValueError("Untrusted signer fingerprint")
        from .domain import Snapshot, TraceSpec
        from .engine import analyze, ENGINE_VERSION

        snap = Snapshot.model_validate_json(z.read("snapshot.json"))
        analysis = json.loads(z.read("analysis.json"))
        cert = analysis["certificate"]
        if cert["engine_version"] == "0.3.0":
            from .legacy.engine_v03 import analyze as replay_engine
        elif cert["engine_version"] == "0.4.0":
            from .legacy.engine_v04 import analyze as replay_engine
        elif cert["engine_version"] == ENGINE_VERSION:
            replay_engine = analyze
        else:
            raise ValueError(
                "Replay requires engine version " + cert["engine_version"] + "; installed " + ENGINE_VERSION
            )
        if cert["engine_version"] in ("0.3.0", "0.4.0") and snap.reconciliation_gaps:
            raise ValueError("Legacy engine cannot replay reconciliation holds")
        replay = replay_engine(snap, TraceSpec.model_validate(cert["specification"]), set(cert["excluded"]))
        if canonical(replay) != canonical(analysis):
            raise ValueError("Analysis replay mismatch")
        return {
            "integrity": "valid",
            "replay": "matched",
            "signer_sha256": fp,
            "identity_trusted": bool(trusted_fingerprint),
            "mode": manifest["mode"],
            "files": len(manifest["files"]),
        }
