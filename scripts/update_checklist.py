"""Refresh unweighted progress counts; never infer or change completion status."""

from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
path = root / "IMPLEMENTATION_CHECKLIST.md"
text = path.read_text(encoding="utf-8")
sections = []
for heading, body in re.findall(r"^## ([A-GX]\. [^\n]+)\n(.*?)(?=^## |\Z)", text, re.M | re.S):
    tasks = re.findall(r"^- \[([ x])\] \*\*([A-GX]\d+)\*\*", body, re.M)
    sections.append((heading, sum(mark == "x" for mark, _ in tasks), len(tasks)))
if not sections:
    raise SystemExit("Checklist sections not found; no file changed")
done = sum(row[1] for row in sections)
total = sum(row[2] for row in sections)
external = sum(row[2] - row[1] for row in sections if row[0].startswith("X."))
summary = [
    f"**{done} of {total} named tasks verified. {total - done} remain: {total - done - external} engineering/validation tasks and {external} external acceptance gates.**",
    "",
    "| Workstream | Verified | Remaining |",
    "|---|---:|---:|",
]
summary.extend(
    f"| {name} | {completed}/{count} | {count - completed} |" for name, completed, count in sections
)
replacement = "<!-- progress:start -->\n" + "\n".join(summary) + "\n<!-- progress:end -->"
updated, changes = re.subn(
    r"<!-- progress:start -->.*?<!-- progress:end -->", lambda _: replacement, text, flags=re.S
)
if changes != 1:
    raise SystemExit("Exactly one progress block required; no file changed")
path.write_text(updated, encoding="utf-8")
print(summary[0].replace("**", ""))
