"""SQLite persistence and fixed-account authentication for the synthetic demo.

This is deliberately not an identity-provider implementation for real workers.
Only validated, allowlisted dashboard state belongs in this generic store.
"""
from __future__ import annotations

import copy
import hashlib
import hmac
import json
import secrets
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable


DEMO_EMAIL = "demo@exaclim.test"
DEMO_PASSWORD = "Exaclim2026!"
_PASSWORD_ROUNDS = 600_000


def _password_hash(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PASSWORD_ROUNDS)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Store:
    """One durable JSON dashboard document, plus independent demo auth tables.

    ``update`` runs a mutator under BEGIN IMMEDIATE and returns its result,
    detached from the stored document. Exceptions roll back the whole mutation.
    A persistent connection keeps ``:memory:`` stores alive between calls.
    """

    def __init__(self, path: str | Path, initial_factory: Callable[[], dict],
                 *, session_ttl_seconds: int = 12 * 60 * 60):
        self.path = str(path)
        self.initial_factory = initial_factory
        self.session_ttl_seconds = session_ttl_seconds
        self._lock = threading.RLock()
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(self.path, timeout=30, isolation_level=None,
                                   check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA busy_timeout = 30000")
        self._db.execute("PRAGMA foreign_keys = ON")
        self._db.execute("PRAGMA journal_mode = WAL")
        self._db.executescript("""
            CREATE TABLE IF NOT EXISTS dashboard_state (
                id INTEGER PRIMARY KEY CHECK(id = 1),
                document TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                salt BLOB NOT NULL,
                password_hash BLOB NOT NULL,
                site_ids TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS session_expiry ON sessions(expires_at);
        """)
        with self._transaction():
            if self._db.execute("SELECT 1 FROM dashboard_state WHERE id=1").fetchone() is None:
                self._save_state(self.initial_factory())
            if self._db.execute("SELECT 1 FROM users WHERE email=?", (DEMO_EMAIL,)).fetchone() is None:
                salt = secrets.token_bytes(32)
                self._db.execute(
                    "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
                    ("demo-supervisor", DEMO_EMAIL, "Demo supervisor", salt,
                     _password_hash(DEMO_PASSWORD, salt), json.dumps(["accra", "tema"])),
                )
        # Also do PBKDF2 work on unknown-user authentication attempts.
        self._dummy_salt = secrets.token_bytes(32)
        self._dummy_hash = _password_hash(secrets.token_urlsafe(32), self._dummy_salt)

    @contextmanager
    def _transaction(self):
        with self._lock:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                yield
                self._db.execute("COMMIT")
            except BaseException:
                self._db.execute("ROLLBACK")
                raise

    def _read_state(self) -> dict:
        row = self._db.execute("SELECT document FROM dashboard_state WHERE id=1").fetchone()
        return json.loads(row["document"])

    def _save_state(self, state: dict):
        if not isinstance(state, dict):
            raise TypeError("Dashboard state must be a dictionary")
        document = json.dumps(state, allow_nan=False, separators=(",", ":"))
        self._db.execute(
            "INSERT INTO dashboard_state(id, document) VALUES(1, ?) "
            "ON CONFLICT(id) DO UPDATE SET document=excluded.document", (document,),
        )

    def load(self) -> dict:
        with self._lock:
            return self._read_state()

    def update(self, fn: Callable[[dict], Any]) -> Any:
        with self._transaction():
            state = self._read_state()
            result = fn(state)
            self._save_state(state)
            return copy.deepcopy(result)

    def reset(self) -> dict:
        """Reset synthetic dashboard state, without resetting identities/sessions."""
        with self._transaction():
            state = self.initial_factory()
            self._save_state(state)
            return copy.deepcopy(state)

    @staticmethod
    def _token_hash(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def authenticate(self, email: str, password: str) -> str | None:
        if not isinstance(email, str) or not isinstance(password, str):
            return None
        if len(email) > 320 or len(password) > 1024:
            return None
        with self._lock:
            row = self._db.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
            salt = row["salt"] if row else self._dummy_salt
            expected = row["password_hash"] if row else self._dummy_hash
            valid = hmac.compare_digest(_password_hash(password, salt), expected)
            if not row or not valid:
                return None
            token = secrets.token_urlsafe(48)
            now = _utcnow()
            expires = now + timedelta(seconds=self.session_ttl_seconds)
            with self._transaction():
                self._db.execute("DELETE FROM sessions WHERE expires_at <= ?", (now.isoformat(),))
                self._db.execute("INSERT INTO sessions VALUES (?, ?, ?, ?)",
                                 (self._token_hash(token), row["id"], now.isoformat(), expires.isoformat()))
            return token

    def user_for_session(self, token: str | None) -> dict | None:
        if not isinstance(token, str) or not token or len(token) > 512:
            return None
        hashed = self._token_hash(token)
        with self._lock:
            row = self._db.execute(
                "SELECT u.id, u.name, u.email, u.site_ids, s.expires_at FROM sessions s "
                "JOIN users u ON u.id=s.user_id WHERE s.token_hash=?", (hashed,),
            ).fetchone()
            if row is None:
                return None
            if datetime.fromisoformat(row["expires_at"]) <= _utcnow():
                self._db.execute("DELETE FROM sessions WHERE token_hash=?", (hashed,))
                return None
            return {"id": row["id"], "name": row["name"], "email": row["email"],
                    "site_ids": json.loads(row["site_ids"])}

    def logout(self, token: str | None) -> None:
        if isinstance(token, str) and token:
            with self._lock:
                self._db.execute("DELETE FROM sessions WHERE token_hash=?", (self._token_hash(token),))

    def grant_site(self, token: str, site_id: str) -> dict | None:
        """Grant the demo supervisor a newly created site; caller authorizes creation."""
        if not isinstance(site_id, str) or not site_id or len(site_id) > 128:
            raise ValueError("Invalid site identifier")
        with self._transaction():
            user = self.user_for_session(token)
            if user is None:
                return None
            if site_id not in user["site_ids"]:
                user["site_ids"].append(site_id)
                self._db.execute("UPDATE users SET site_ids=? WHERE id=?",
                                 (json.dumps(user["site_ids"]), user["id"]))
            return copy.deepcopy(user)

    def close(self):
        with self._lock:
            self._db.close()
