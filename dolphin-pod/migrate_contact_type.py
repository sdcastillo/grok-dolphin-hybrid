#!/usr/bin/env python3
"""Add contact_type to customers + invites. Safe to re-run."""
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
    if "contact_type" not in columns(conn, "customers"):
        conn.execute("ALTER TABLE customers ADD COLUMN contact_type TEXT")
        print("added customers.contact_type")
    if "contact_type" not in columns(conn, "invites"):
        conn.execute("ALTER TABLE invites ADD COLUMN contact_type TEXT")
        print("added invites.contact_type")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_type ON customers(contact_type)")
    conn.execute("DROP VIEW IF EXISTS customer_devices")
    conn.executescript(VIEW_SQL)
    # owner row: you, not a contact bucket
    conn.execute(
        """UPDATE customers SET contact_type='self', updated_at=datetime('now')
           WHERE contact_type IS NULL AND (
             email IN ('castillo.sam.d@gmail.com','samuel.castillo@predictiveinsightsai.com')
             OR (first_name LIKE 'Sam%' AND last_name='Castillo')
           )"""
    )
    conn.commit()
    print(f"migrated {DB}")
    conn.close()


if __name__ == "__main__":
    main()
