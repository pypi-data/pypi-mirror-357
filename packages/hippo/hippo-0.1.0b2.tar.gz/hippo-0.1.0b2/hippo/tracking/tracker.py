"""Very small experiment tracker (no external DB)."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

_DB = Path.home() / ".hippo" / "runs.sqlite"
_DB.parent.mkdir(exist_ok=True)


class Tracker:
    """Context-manager for logging parameters and metrics."""

    def __init__(self, run_name: str):
        self.run_name = run_name
        self.conn = sqlite3.connect(_DB)
        self._ensure_tables()

    def _ensure_tables(self):
        with self.conn as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    started_at TEXT
                )"""
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    run_id INTEGER,
                    key TEXT,
                    value REAL
                )"""
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS params (
                    run_id INTEGER,
                    key TEXT,
                    value TEXT
                )"""
            )

    @contextmanager
    def start(self):
        with self.conn as conn:
            cur = conn.execute(
                "INSERT INTO runs(name, started_at) VALUES (?, ?)",
                (self.run_name, datetime.utcnow().isoformat()),
            )
            run_id = cur.lastrowid
        try:
            yield lambda k, v: self._log_metric(run_id, k, v), lambda k, v: self._log_param(
                run_id, k, v
            )
        finally:
            self.conn.close()

    def _log_metric(self, run_id: int, key: str, value: float):
        with self.conn:
            self.conn.execute(
                "INSERT INTO metrics(run_id, key, value) VALUES (?, ?, ?)",
                (run_id, key, value),
            )

    def _log_param(self, run_id: int, key: str, value: Any):
        with self.conn:
            self.conn.execute(
                "INSERT INTO params(run_id, key, value) VALUES (?, ?, ?)",
                (run_id, key, str(value)),
            )
