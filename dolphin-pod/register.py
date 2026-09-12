#!/usr/bin/env python3
"""Register a customer and/or device on DOLPHIN POD."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "dolphin_pod.sqlite"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def upsert_customer(conn, first, last, email=None, phone=None, display=None, role="member", notes=None) -> int:
    display = display or f"{first} {last}"
    if email:
        row = conn.execute("SELECT id FROM customers WHERE email = ?", (email,)).fetchone()
        if row:
            conn.execute(
                """UPDATE customers SET first_name=?, last_name=?, display_name=?, phone=COALESCE(?, phone),
                   role=?, notes=COALESCE(?, notes), updated_at=datetime('now') WHERE id=?""",
                (first, last, display, phone, role, notes, row["id"]),
            )
            return row["id"]
    cur = conn.execute(
        """INSERT INTO customers (first_name, last_name, display_name, email, phone, role, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (first, last, display, email, phone, role, notes),
    )
    return cur.lastrowid


def upsert_device(conn, customer_id, name, ip=None, ipv6=None, os=None, online=0, last_seen=None) -> int:
    row = conn.execute("SELECT id FROM devices WHERE tailscale_name = ?", (name,)).fetchone()
    if row:
        conn.execute(
            """UPDATE devices SET customer_id=?, tailscale_ip=COALESCE(?, tailscale_ip),
               tailscale_ipv6=COALESCE(?, tailscale_ipv6), os=COALESCE(?, os),
               online=?, last_seen=COALESCE(?, last_seen), updated_at=datetime('now') WHERE id=?""",
            (customer_id, ip, ipv6, os, online, last_seen, row["id"]),
        )
        return row["id"]
    cur = conn.execute(
        """INSERT INTO devices (customer_id, tailscale_name, tailscale_ip, tailscale_ipv6, os, online, last_seen)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (customer_id, name, ip, ipv6, os, online, last_seen),
    )
    return cur.lastrowid


def add_invite(conn, email, first=None, last=None, role="dev"):
    import secrets
    token = secrets.token_urlsafe(16)
    conn.execute(
        """INSERT INTO invites (email, first_name, last_name, role, token, status)
           VALUES (?, ?, ?, ?, ?, 'pending')""",
        (email, first, last, role, token),
    )
    return token


def list_invites(conn):
    rows = conn.execute(
        "SELECT id, email, first_name, last_name, role, status, created_at FROM invites ORDER BY id"
    ).fetchall()
    if not rows:
        print("(no invites)")
        return
    print(f"{'id':<4} {'status':<10} {'role':<8} {'email':<36} {'name'}")
    for r in rows:
        name = " ".join(x for x in (r["first_name"], r["last_name"]) if x)
        print(f"{r['id']:<4} {r['status']:<10} {r['role']:<8} {(r['email'] or ''):<36} {name}")


def list_all(conn):
    rows = conn.execute("SELECT * FROM customer_devices ORDER BY last_name, first_name, tailscale_name").fetchall()
    if not rows:
        print("(empty)")
        return
    print(f"{'name':<28} {'email':<36} {'phone':<16} {'machine':<18} {'ip':<16}")
    for r in rows:
        print(
            f"{(r['name'] or ''):<28} {(r['email'] or ''):<36} {(r['phone'] or ''):<16} "
            f"{(r['tailscale_name'] or ''):<18} {(r['tailscale_ip'] or ''):<16}"
        )


def main():
    p = argparse.ArgumentParser(description="DOLPHIN POD customer/device registry")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add", help="register a person")
    a.add_argument("--first", required=True)
    a.add_argument("--last", required=True)
    a.add_argument("--email")
    a.add_argument("--phone")
    a.add_argument("--display")
    a.add_argument("--role", default="member")
    a.add_argument("--machine", help="Tailscale hostname")
    a.add_argument("--ip")
    a.add_argument("--os")
    sub.add_parser("list", help="print registry")
    inv = sub.add_parser("invite", help="queue a pending teammate invite")
    inv.add_argument("--email", required=True)
    inv.add_argument("--first")
    inv.add_argument("--last")
    inv.add_argument("--role", default="dev")
    sub.add_parser("invites", help="list invites")
    args = p.parse_args()
    conn = connect()
    if args.cmd == "list":
        list_all(conn)
        return
    if args.cmd == "invites":
        list_invites(conn)
        return
    if args.cmd == "invite":
        token = add_invite(conn, args.email, args.first, args.last, args.role)
        conn.commit()
        print(f"pending invite for {args.email}")
        print(f"token={token}")
        print("They still must accept a Tailscale invite in the admin console.")
        list_invites(conn)
        return
    cid = upsert_customer(conn, args.first, args.last, args.email, args.phone, args.display, args.role)
    if args.machine:
        upsert_device(conn, cid, args.machine, args.ip, os=args.os)
    conn.commit()
    print(f"customer_id={cid}")
    list_all(conn)


if __name__ == "__main__":
    main()
