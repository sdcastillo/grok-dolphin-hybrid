#!/usr/bin/env python3
"""Local DOLPHIN POD / Rolladex server. No public funnel. No location."""
from __future__ import annotations

import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DIR = Path(__file__).resolve().parent
DB = DIR / "dolphin_pod.sqlite"
HOST = "127.0.0.1"
PORT = 8787


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def rebuild() -> None:
    import subprocess
    import sys

    for script in ("migrate_contact_type.py", "migrate_rolodex.py", "migrate_outreach.py", "rolodex.py", "outreach.py", "status_html.py"):
        p = DIR / script
        if p.exists():
            subprocess.run([sys.executable, str(p)], check=False, cwd=DIR)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        print("[%s] " % self.log_date_time_string() + (fmt % args))

    def send_file(self, path: Path, ctype: str) -> None:
        if not path.exists():
            self.send_error(404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in ("/", "/rolodex", "/rolodex.html"):
            rebuild()
            self.send_file(DIR / "rolodex.html", "text/html; charset=utf-8")
            return
        if path in ("/outreach", "/outreach.html", "/table"):
            rebuild()
            self.send_file(DIR / "outreach.html", "text/html; charset=utf-8")
            return
        if path in ("/status", "/status.html"):
            rebuild()
            self.send_file(DIR / "status.html", "text/html; charset=utf-8")
            return
        if path == "/outreach.csv":
            rebuild()
            self.send_file(DIR / "outreach.csv", "text/csv; charset=utf-8")
            return
        if path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true,"service":"dolphin-pod"}')
            return
        self.send_error(404)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/reply":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8")
        ctype = self.headers.get("Content-Type") or ""
        if "json" in ctype:
            body = json.loads(raw or "{}")
        else:
            body = {k: (v[0] if v else "") for k, v in parse_qs(raw).items()}
        email = (body.get("email") or "").strip()
        if not email:
            self.send_error(400, "email required")
            return
        conn = connect()
        cust = conn.execute("SELECT id FROM customers WHERE email=?", (email,)).fetchone()
        if not cust:
            conn.close()
            self.send_error(404, "no customer")
            return
        fields = {
            k: (body.get(k) or None)
            for k in (
                "channel",
                "sent_at",
                "who_replied",
                "replied_at",
                "time_to_reply",
                "follow_up_at",
                "outcome",
                "notes",
            )
        }
        existing = conn.execute(
            "SELECT id FROM outreach WHERE customer_id=? ORDER BY id DESC LIMIT 1",
            (cust["id"],),
        ).fetchone()
        sets = {k: v for k, v in fields.items() if v is not None}
        if existing:
            if sets:
                cols = ", ".join(f"{k}=?" for k in sets)
                conn.execute(
                    f"UPDATE outreach SET {cols}, updated_at=datetime('now') WHERE id=?",
                    [*sets.values(), existing["id"]],
                )
        else:
            conn.execute(
                """INSERT INTO outreach (customer_id, channel, sent_at, who_replied, replied_at,
                     time_to_reply, follow_up_at, outcome, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    cust["id"],
                    fields["channel"],
                    fields["sent_at"],
                    fields["who_replied"],
                    fields["replied_at"],
                    fields["time_to_reply"],
                    fields["follow_up_at"],
                    fields["outcome"] or "pending",
                    fields["notes"],
                ),
            )
        conn.commit()
        conn.close()
        rebuild()
        self.send_response(303)
        self.send_header("Location", "/outreach")
        self.end_headers()


def main() -> None:
    rebuild()
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"DOLPHIN POD listening on http://{HOST}:{PORT}")
    print("  /rolodex   cards")
    print("  /outreach  reply table")
    print("  /status    machines")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
