"""Operator entry point from the repository root; no installed package needed."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from vasp_app.manage import main  # noqa: E402

raise SystemExit(main())
