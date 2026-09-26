"""Local operator commands. No credentials are printed or accepted as CLI arguments."""
import argparse
import json
import signal
import sys
from .config import settings
from .store import engine
from .migrations import upgrade, require_current, revision


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m vasp_app.manage")
    commands = parser.add_subparsers(dest="command", required=True)
    migration = commands.add_parser("db-upgrade", help="Apply versioned migrations to the configured database")
    migration.add_argument("--adopt-legacy", action="store_true", help="Adopt only an exact original schema; back up first")
    commands.add_parser("db-version")
    commands.add_parser("worker", help="Run a separate durable worker process")
    commands.add_parser("readiness")
    args = parser.parse_args(argv)
    try:
        if args.command == "db-upgrade":
            print(json.dumps({"revision": upgrade(engine, adopt_legacy=args.adopt_legacy)}))
        elif args.command == "db-version":
            with engine.connect() as conn:
                print(json.dumps({"revision": revision(conn)}))
        elif args.command == "readiness":
            from .observability import readiness
            result = readiness()
            print(json.dumps(result))
            return 0 if result["ready"] else 1
        elif args.command == "worker":
            from . import worker
            from .observability import configure_logging
            if settings.auto_migrate:
                upgrade(engine)
            require_current(engine)
            configure_logging()
            for sig in (signal.SIGINT, signal.SIGTERM):
                signal.signal(sig, lambda *_: worker.stop_event.set())
            worker.loop()
        return 0
    except Exception as exc:
        # SQL/connection errors may contain DSNs. Report their category only.
        print(json.dumps({"error": type(exc).__name__, "message": "Operation failed; check configuration, database/schema and operator guide"}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
