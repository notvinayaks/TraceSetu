from __future__ import annotations
import base64
import hashlib
import hmac
import secrets
from sqlalchemy import select
from fastapi import Depends, HTTPException, Request
from .store import User, Session, SessionLocal, Record, uid, now
from .config import settings


def password_hash(password):
    salt = secrets.token_bytes(16)
    hashed = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1, dklen=32)
    return base64.b64encode(salt + hashed).decode()


def check_password(password, encoded):
    try:
        data = base64.b64decode(encoded)
        return hmac.compare_digest(
            data[16:], hashlib.scrypt(password.encode(), salt=data[:16], n=16384, r=8, p=1, dklen=32)
        )
    except (ValueError, TypeError):
        return False


def session_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


def get_db():
    with SessionLocal() as db:
        yield db


def principal(request: Request, db=Depends(get_db)):
    token = request.cookies.get("atlas_session", "")
    s = db.get(Session, session_hash(token)) if token else None
    if not s or s.expires < now():
        raise HTTPException(401, "Sign in to continue.")
    user = db.get(User, s.user_id)
    if not user or not user.active:
        raise HTTPException(401, "Session unavailable.")
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        if not hmac.compare_digest(request.headers.get("X-CSRF-Token", ""), s.csrf):
            raise HTTPException(403, "Invalid request token. Reload and retry.")
    request.state.user = user
    request.state.session = s
    return user


def require_role(user, *roles):
    if user.role not in roles:
        raise HTTPException(403, "Your role cannot perform this action.")


def case_access(db, user, case_id):
    case = db.get(Record, case_id)
    if not case or case.kind != "case" or case.tenant != user.tenant:
        raise HTTPException(404, "Case not found.")
    if user.role != "admin" and user.id not in case.payload.get("members", []):
        raise HTTPException(404, "Case not found.")
    return case


def object_access(db, user, id, kind=None):
    r = db.get(Record, id)
    if not r or r.tenant != user.tenant or (kind and r.kind != kind):
        raise HTTPException(404, "Record not found.")
    if r.case_id:
        case_access(db, user, r.case_id)
    return r


def bootstrap(db):
    if not settings.local_bootstrap or db.scalar(select(User).limit(1)):
        return
    rows = []
    for username, role in [("admin", "admin"), ("investigator", "investigator"), ("reviewer", "reviewer")]:
        password = secrets.token_urlsafe(18)
        u = User(
            id=uid("usr_"),
            tenant="local-agency",
            username=username,
            display_name=username.title(),
            password_hash=password_hash(password),
            role=role,
        )
        db.add(u)
        rows.append(f"{username}: {password}")
    db.commit()
    p = settings.data_dir / "bootstrap-credentials.txt"
    p.write_text(
        "LOCAL DEVELOPMENT ACCOUNTS\nRotate before any operational deployment. Do not share or commit this file.\n\n"
        + "\n".join(rows)
        + "\n",
        encoding="utf-8",
    )
