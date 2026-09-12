#!/usr/bin/env python3
"""Add org + title for the Rolladex. Safe to re-run."""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "dolphin_pod.sqlite"

VIEW_SQL = """
CREATE VIEW IF NOT EXISTS customer_devices AS
SELECT
  c.id AS customer_id,
  c.first_name,
  c.last_name,
  COALESCE(c.display_name, c.first_name || ' ' || c.last_name) AS name,
  c.email,
  c.phone,
  c.role,
  c.contact_type,
  c.org,
  c.title,
  c.notes,
  d.id AS device_id,
  d.tailscale_name,
  d.tailscale_ip,
  d.os,
  d.online,
  d.last_seen
FROM customers c
LEFT JOIN devices d ON d.customer_id = c.id;
"""


def columns(conn, table: str) -> set[str]:
    return {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}


def main() -> None:
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    cols = columns(conn, "customers")
    if "org" not in cols:
        conn.execute("ALTER TABLE customers ADD COLUMN org TEXT")
        print("added customers.org")
    if "title" not in cols:
        conn.execute("ALTER TABLE customers ADD COLUMN title TEXT")
        print("added customers.title")
    conn.execute("DROP VIEW IF EXISTS customer_devices")
    conn.executescript(VIEW_SQL)
    conn.commit()
    print(f"migrated {DB}")
    conn.close()


if __name__ == "__main__":
    main()
