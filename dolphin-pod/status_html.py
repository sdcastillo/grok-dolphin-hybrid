#!/usr/bin/env python3
"""Write a local-only DOLPHIN POD status page. No location fields."""
from __future__ import annotations

import html
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
DB = DIR / "dolphin_pod.sqlite"
OUT = DIR / "status.html"


def rows(sql: str, args=()):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(sql, args).fetchall()
    finally:
        conn.close()


def esc(v) -> str:
    return html.escape("" if v is None else str(v))


def main() -> None:
    people = rows(
        """SELECT id, COALESCE(display_name, first_name || ' ' || last_name) AS name,
                  email, phone, role FROM customers ORDER BY last_name, first_name"""
    )
    devices = rows(
        """SELECT customer_id, tailscale_name, tailscale_ip, os, online, last_seen
           FROM devices ORDER BY tailscale_name"""
    )
    invites = rows(
        "SELECT email, first_name, last_name, role, status, created_at FROM invites ORDER BY id"
    )
    by_cust: dict[int, list] = {}
    for d in devices:
        by_cust.setdefault(d["customer_id"], []).append(d)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    online = sum(1 for d in devices if d["online"])
    pending = sum(1 for i in invites if i["status"] == "pending")

    parts = [
        "<!DOCTYPE html>",
        "<html lang='en'><head><meta charset='utf-8'>",
        "<title>DOLPHIN POD</title>",
        "<style>",
        "body{font-family:ui-sans-serif,system-ui,sans-serif;background:#0b1220;color:#e8eef8;margin:2rem;}",
        "h1{letter-spacing:.08em;font-size:1.2rem;}",
        "h2{margin-top:2rem;font-size:1rem;color:#9fb3d1;}",
        ".meta{color:#7f93b0;font-size:.9rem;}",
        "table{border-collapse:collapse;width:100%;max-width:960px;}",
        "th,td{text-align:left;padding:.4rem .6rem;border-bottom:1px solid #1d2a44;}",
        "th{color:#9fb3d1;font-weight:600;}",
        ".on{color:#5ee0a8;} .off{color:#8a97ad;}",
        ".note{color:#7f93b0;margin-top:2rem;font-size:.85rem;}",
        "</style></head><body>",
        "<h1>DOLPHIN POD</h1>",
        f"<p class='meta'>{esc(now)} · {len(people)} people · {len(devices)} devices "
        f"({online} online) · {pending} pending invites · no location stored</p>",
        "<h2>People + machines</h2>",
        "<table><tr><th>Name</th><th>Email</th><th>Phone</th><th>Role</th>"
        "<th>Machine</th><th>IP</th><th>OS</th><th>State</th></tr>",
    ]
    if not people:
        parts.append("<tr><td colspan='8'>(empty)</td></tr>")
    for c in people:
        devs = by_cust.get(c["id"]) or [None]
        for i, d in enumerate(devs):
            name = esc(c["name"]) if i == 0 else ""
            email = esc(c["email"]) if i == 0 else ""
            phone = esc(c["phone"]) if i == 0 else ""
            role = esc(c["role"]) if i == 0 else ""
            if d is None:
                parts.append(
                    f"<tr><td>{name}</td><td>{email}</td><td>{phone}</td><td>{role}</td>"
                    "<td colspan='4'>(no devices)</td></tr>"
                )
            else:
                state = "online" if d["online"] else "offline"
                cls = "on" if d["online"] else "off"
                parts.append(
                    f"<tr><td>{name}</td><td>{email}</td><td>{phone}</td><td>{role}</td>"
                    f"<td>{esc(d['tailscale_name'])}</td><td>{esc(d['tailscale_ip'])}</td>"
                    f"<td>{esc(d['os'])}</td><td class='{cls}'>{state}</td></tr>"
                )
    parts.append("</table>")
    parts.append("<h2>Invites</h2><table><tr><th>Status</th><th>Role</th><th>Email</th><th>Name</th><th>Created</th></tr>")
    if not invites:
        parts.append("<tr><td colspan='5'>(no invites)</td></tr>")
    for i in invites:
        name = " ".join(x for x in (i["first_name"], i["last_name"]) if x)
        parts.append(
            f"<tr><td>{esc(i['status'])}</td><td>{esc(i['role'])}</td><td>{esc(i['email'])}</td>"
            f"<td>{esc(name)}</td><td>{esc(i['created_at'])}</td></tr>"
        )
    parts.extend(
        [
            "</table>",
            "<p class='note'>Local file only. Exact location is not stored. Andy and other unregistered nodes stay off this page until they opt in.</p>",
            "</body></html>",
        ]
    )
    OUT.write_text("\n".join(parts) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
