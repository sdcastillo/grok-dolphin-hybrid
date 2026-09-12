#!/usr/bin/env python3
"""Refresh DOLPHIN POD device rows from `tailscale status --json`.

Only updates machines already in `devices`. Unknown nodes are printed
as unregistered — they are NOT auto-added (no silent tracking).
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
from pathlib import Path

DB = Path(__file__).resolve().parent / "dolphin_pod.sqlite"
SKIP_PREFIXES = ("funnel-ingress-node",)


def status() -> dict:
    out = subprocess.check_output(["tailscale", "status", "--json"], text=True)
    return json.loads(out)


def peers(data: dict) -> list[dict]:
    rows = []
    self = data.get("Self") or {}
    if self.get("HostName"):
        rows.append(self)
    for p in (data.get("Peer") or {}).values():
        rows.append(p)
    return rows


def main() -> None:
    data = status()
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    updated = 0
    unknown = []
    for p in peers(data):
        host = (p.get("HostName") or "").strip()
        dns = (p.get("DNSName") or "").split(".")[0]
        name = dns or host
        if not name or name.startswith(SKIP_PREFIXES):
            continue
        ips = p.get("TailscaleIPs") or []
        ip4 = next((i for i in ips if ":" not in i), None)
        ip6 = next((i for i in ips if ":" in i), None)
        online = 1 if p.get("Online") else 0
        last = p.get("LastSeen") or None
        if last and last.startswith("0001-"):
            last = None
        row = conn.execute("SELECT id FROM devices WHERE tailscale_name = ?", (name,)).fetchone()
        if not row and name != host:
            row = conn.execute("SELECT id FROM devices WHERE tailscale_name = ?", (host,)).fetchone()
            if row:
                name = host
        if not row:
            unknown.append((name, ip4, p.get("OS"), online))
            continue
        conn.execute(
            """UPDATE devices SET tailscale_ip=COALESCE(?, tailscale_ip),
               tailscale_ipv6=COALESCE(?, tailscale_ipv6), os=COALESCE(?, os),
               online=?, last_seen=COALESCE(?, last_seen), updated_at=datetime('now')
               WHERE id=?""",
            (ip4, ip6, p.get("OS"), online, last, row["id"]),
        )
        updated += 1
    conn.commit()
    print(f"updated {updated} registered device(s)")
    if unknown:
        print("unregistered (not added):")
        for n, ip, os, on in unknown:
            print(f"  {n:20} {ip or '-':16} {os or '-':8} {'online' if on else 'offline'}")


if __name__ == "__main__":
    main()
