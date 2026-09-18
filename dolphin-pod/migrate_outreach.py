#!/usr/bin/env python3
"""Add outreach/reply-tracking table. Safe to re-run."""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "dolphin_pod.sqlite"

SQL = """
CREATE TABLE IF NOT EXISTS outreach (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id     INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  channel         TEXT,          -- email | phone | text | in-person | other
  sent_at         TEXT,          -- when you reached out
  who_replied     TEXT,          -- name of person who replied (blank until then)
  replied_at      TEXT,          -- when they replied
  time_to_reply   TEXT,          -- fill later, e.g. 2d 4h
  follow_up_at    TEXT,          -- next follow-up date
  outcome         TEXT,          -- pending | replied | no-reply | closed
  notes           TEXT,
  created_at      TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_outreach_customer ON outreach(customer_id);
"""


def main() -> None:
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SQL)
    # one empty tracking row per contact who isn't you, if none exists yet
    conn.execute(
        """INSERT INTO outreach (customer_id, outcome)
           SELECT c.id, 'pending'
           FROM customers c
           WHERE NOT EXISTS (SELECT 1 FROM outreach o WHERE o.customer_id = c.id)"""
    )
    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM outreach").fetchone()[0]
    print(f"migrated {DB} ({n} outreach row(s))")
    conn.close()


if __name__ == "__main__":
    main()
