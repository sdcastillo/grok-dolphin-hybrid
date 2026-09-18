#!/usr/bin/env python3
"""Register a customer and/or device on DOLPHIN POD."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "dolphin_pod.sqlite"

# role = mesh privilege. contact_type = relationship bucket (private).
CONTACT_TYPES = {
    "self": "you",
    "business": "business",
    "client": "client",
    "manager": "future boss / manager",
    "researcher": "student / researcher",
    "romantic": "romantic / spouse potential",
}
ALIASES = {
    "boss": "manager",
    "future boss": "manager",
    "future-boss": "manager",
    "future boss and manager": "manager",
    "student": "researcher",
    "student or researcher": "researcher",
    "research": "researcher",
    "spouse": "romantic",
    "dating": "romantic",
    "romantic spouse potential": "romantic",
    "me": "self",
    "owner": "self",
}


def normalize_type(value: str | None) -> str | None:
    if value is None or value.strip() == "":
        return None
    key = value.strip().lower()
    key = ALIASES.get(key, key)
    if key not in CONTACT_TYPES:
        allowed = ", ".join(CONTACT_TYPES)
        raise SystemExit(f"unknown contact type {value!r}. use: {allowed}")
    return key


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def upsert_customer(
    conn,
    first,
    last,
    email=None,
    phone=None,
    display=None,
    role="member",
    notes=None,
    contact_type=None,
    org=None,
    title=None,
) -> int:
    display = display or f"{first} {last}"
    contact_type = normalize_type(contact_type)
    if email:
        row = conn.execute("SELECT id FROM customers WHERE email = ?", (email,)).fetchone()
        if row:
            conn.execute(
                """UPDATE customers SET first_name=?, last_name=?, display_name=?, phone=COALESCE(?, phone),
                   role=?, notes=COALESCE(?, notes), org=COALESCE(?, org), title=COALESCE(?, title),
                   contact_type=COALESCE(?, contact_type), updated_at=datetime('now') WHERE id=?""",
                (first, last, display, phone, role, notes, org, title, contact_type, row["id"]),
            )
            return row["id"]
    cur = conn.execute(
        """INSERT INTO customers (first_name, last_name, display_name, email, phone, role, notes, contact_type, org, title)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (first, last, display, email, phone, role, notes, contact_type, org, title),
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


def add_invite(conn, email, first=None, last=None, role="dev", contact_type=None):
    import secrets

    token = secrets.token_urlsafe(16)
    contact_type = normalize_type(contact_type)
    conn.execute(
        """INSERT INTO invites (email, first_name, last_name, role, contact_type, token, status)
           VALUES (?, ?, ?, ?, ?, ?, 'pending')""",
        (email, first, last, role, contact_type, token),
    )
    return token


def list_invites(conn):
    rows = conn.execute(
        "SELECT id, email, first_name, last_name, role, contact_type, status, created_at FROM invites ORDER BY id"
    ).fetchall()
    if not rows:
        print("(no invites)")
        return
    print(f"{'id':<4} {'status':<10} {'type':<12} {'role':<8} {'email':<36} {'name'}")
    for r in rows:
        name = " ".join(x for x in (r["first_name"], r["last_name"]) if x)
        print(
            f"{r['id']:<4} {r['status']:<10} {(r['contact_type'] or ''):<12} {r['role']:<8} "
            f"{(r['email'] or ''):<36} {name}"
        )


def accept_invite(conn, email=None, token=None, phone=None, machine=None, ip=None, os=None, contact_type=None) -> int:
    if token:
        inv = conn.execute("SELECT * FROM invites WHERE token = ? AND status = 'pending'", (token,)).fetchone()
    elif email:
        inv = conn.execute(
            "SELECT * FROM invites WHERE email = ? AND status = 'pending' ORDER BY id DESC LIMIT 1",
            (email,),
        ).fetchone()
    else:
        raise SystemExit("accept needs --email or --token")
    if not inv:
        raise SystemExit("no pending invite")
    first = inv["first_name"] or "Pending"
    last = inv["last_name"] or "Member"
    ctype = contact_type or inv["contact_type"]
    cid = upsert_customer(conn, first, last, inv["email"], phone, role=inv["role"] or "dev", contact_type=ctype)
    if machine:
        upsert_device(conn, cid, machine, ip, os=os)
    conn.execute(
        "UPDATE invites SET status='accepted', accepted_at=datetime('now') WHERE id=?",
        (inv["id"],),
    )
    return cid


def export_csv(conn, path: str) -> None:
    import csv

    rows = conn.execute("SELECT * FROM customer_devices ORDER BY last_name, first_name").fetchall()
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "name",
                "first_name",
                "last_name",
                "email",
                "phone",
                "role",
                "contact_type",
                "tailscale_name",
                "tailscale_ip",
                "os",
                "online",
                "last_seen",
            ]
        )
        for r in rows:
            w.writerow(
                [
                    r["name"],
                    r["first_name"],
                    r["last_name"],
                    r["email"],
                    r["phone"],
                    r["role"] if "role" in r.keys() else "",
                    r["contact_type"] if "contact_type" in r.keys() else "",
                    r["tailscale_name"],
                    r["tailscale_ip"],
                    r["os"],
                    r["online"],
                    r["last_seen"],
                ]
            )
    print(f"wrote {path} ({len(rows)} rows)")


def revoke_invite(conn, email=None, token=None, invite_id=None) -> int:
    if token:
        cur = conn.execute(
            "UPDATE invites SET status='revoked' WHERE token=? AND status='pending'",
            (token,),
        )
    elif invite_id is not None:
        cur = conn.execute(
            "UPDATE invites SET status='revoked' WHERE id=? AND status='pending'",
            (invite_id,),
        )
    elif email:
        cur = conn.execute(
            "UPDATE invites SET status='revoked' WHERE email=? AND status='pending'",
            (email,),
        )
    else:
        raise SystemExit("revoke needs --email, --token, or --id")
    if cur.rowcount == 0:
        raise SystemExit("no pending invite to revoke")
    return cur.rowcount


def who(conn, q: str) -> None:
    like = f"%{q}%"
    people = conn.execute(
        """SELECT DISTINCT c.id, COALESCE(c.display_name, c.first_name || ' ' || c.last_name) AS name,
                  c.email, c.phone, c.role, c.contact_type
           FROM customers c
           LEFT JOIN devices d ON d.customer_id = c.id
           WHERE c.first_name LIKE ? OR c.last_name LIKE ? OR c.display_name LIKE ?
              OR c.email LIKE ? OR c.phone LIKE ? OR d.tailscale_name LIKE ?
              OR d.tailscale_ip LIKE ? OR IFNULL(c.contact_type,'') LIKE ?
           ORDER BY c.last_name, c.first_name""",
        (like, like, like, like, like, like, like, like),
    ).fetchall()
    if not people:
        print(f"(no match for {q!r})")
        return
    for c in people:
        print(
            f"{c['name']}  {c['email'] or ''}  {c['phone'] or ''}  "
            f"type={c['contact_type'] or '-'}  role={c['role']}"
        )
        devs = conn.execute(
            "SELECT tailscale_name, tailscale_ip, os, online, last_seen FROM devices WHERE customer_id=? ORDER BY tailscale_name",
            (c["id"],),
        ).fetchall()
        if not devs:
            print("  (no devices)")
        for d in devs:
            on = "online" if d["online"] else "offline"
            print(
                f"  {d['tailscale_name']:<18} {(d['tailscale_ip'] or ''):<16} "
                f"{(d['os'] or ''):<8} {on}  {d['last_seen'] or ''}"
            )


def set_type(conn, contact_type: str, email=None, query=None) -> int:
    contact_type = normalize_type(contact_type)
    if email:
        cur = conn.execute(
            "UPDATE customers SET contact_type=?, updated_at=datetime('now') WHERE email=?",
            (contact_type, email),
        )
    elif query:
        like = f"%{query}%"
        cur = conn.execute(
            """UPDATE customers SET contact_type=?, updated_at=datetime('now')
               WHERE first_name LIKE ? OR last_name LIKE ? OR display_name LIKE ? OR email LIKE ?""",
            (contact_type, like, like, like, like),
        )
    else:
        raise SystemExit("set-type needs --email or --name")
    if cur.rowcount == 0:
        raise SystemExit("no matching customer")
    return cur.rowcount


def list_types() -> None:
    print(f"{'slug':<14} {'meaning'}")
    for k, v in CONTACT_TYPES.items():
        print(f"{k:<14} {v}")



def list_outreach(conn):
    rows = conn.execute(
        """SELECT o.id, COALESCE(c.display_name, c.first_name || ' ' || c.last_name) AS name,
                  c.contact_type, o.channel, o.sent_at, o.who_replied, o.replied_at,
                  o.time_to_reply, o.follow_up_at, o.outcome
           FROM outreach o JOIN customers c ON c.id = o.customer_id
           ORDER BY o.id"""
    ).fetchall()
    print(f"{'id':<4} {'type':<12} {'name':<22} {'sent':<12} {'who_replied':<16} {'time_to_reply':<14} {'outcome'}")
    if not rows:
        print("(no outreach rows)")
        return
    for r in rows:
        print(
            f"{r['id']:<4} {(r['contact_type'] or ''):<12} {(r['name'] or ''):<22} "
            f"{(r['sent_at'] or ''):<12} {(r['who_replied'] or ''):<16} "
            f"{(r['time_to_reply'] or ''):<14} {r['outcome'] or ''}"
        )


def set_reply(conn, email=None, name=None, who_replied=None, replied_at=None,
              sent_at=None, channel=None, time_to_reply=None, follow_up_at=None,
              outcome=None, notes=None) -> int:
    if email:
        row = conn.execute("SELECT id FROM customers WHERE email=?", (email,)).fetchone()
    elif name:
        like = f"%{name}%"
        row = conn.execute(
            "SELECT id FROM customers WHERE first_name LIKE ? OR last_name LIKE ? OR display_name LIKE ?",
            (like, like, like),
        ).fetchone()
    else:
        raise SystemExit("reply needs --email or --name")
    if not row:
        raise SystemExit("no matching customer")
    cid = row["id"]
    existing = conn.execute(
        "SELECT id FROM outreach WHERE customer_id=? ORDER BY id DESC LIMIT 1", (cid,)
    ).fetchone()
    fields = {
        "who_replied": who_replied,
        "replied_at": replied_at,
        "sent_at": sent_at,
        "channel": channel,
        "time_to_reply": time_to_reply,
        "follow_up_at": follow_up_at,
        "outcome": outcome,
        "notes": notes,
    }
    sets = {k: v for k, v in fields.items() if v is not None}
    if existing:
        if not sets:
            return existing["id"]
        cols = ", ".join(f"{k}=?" for k in sets)
        conn.execute(
            f"UPDATE outreach SET {cols}, updated_at=datetime('now') WHERE id=?",
            [*sets.values(), existing["id"]],
        )
        return existing["id"]
    conn.execute(
        """INSERT INTO outreach (customer_id, channel, sent_at, who_replied, replied_at,
             time_to_reply, follow_up_at, outcome, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (cid, channel, sent_at, who_replied, replied_at, time_to_reply, follow_up_at, outcome or "pending", notes),
    )
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def list_all(conn, contact_type=None):
    contact_type = normalize_type(contact_type)
    if contact_type:
        rows = conn.execute(
            "SELECT * FROM customer_devices WHERE contact_type=? ORDER BY last_name, first_name, tailscale_name",
            (contact_type,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM customer_devices ORDER BY contact_type, last_name, first_name, tailscale_name"
        ).fetchall()
    if not rows:
        print("(empty)")
        return
    print(f"{'type':<12} {'name':<24} {'email':<32} {'phone':<16} {'machine':<18} {'ip':<16}")
    for r in rows:
        print(
            f"{(r['contact_type'] or ''):<12} {(r['name'] or ''):<24} {(r['email'] or ''):<32} "
            f"{(r['phone'] or ''):<16} {(r['tailscale_name'] or ''):<18} {(r['tailscale_ip'] or ''):<16}"
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
    a.add_argument("--type", dest="contact_type", help="business|client|manager|researcher|romantic|self")
    a.add_argument("--org")
    a.add_argument("--title")
    a.add_argument("--notes")
    a.add_argument("--machine", help="Tailscale hostname")
    a.add_argument("--ip")
    a.add_argument("--os")
    lst = sub.add_parser("list", help="print registry")
    lst.add_argument("--type", dest="contact_type")
    inv = sub.add_parser("invite", help="queue a pending teammate invite")
    inv.add_argument("--email", required=True)
    inv.add_argument("--first")
    inv.add_argument("--last")
    inv.add_argument("--role", default="dev")
    inv.add_argument("--type", dest="contact_type")
    sub.add_parser("invites", help="list invites")
    acc = sub.add_parser("accept", help="turn a pending invite into a customer")
    acc.add_argument("--email")
    acc.add_argument("--token")
    acc.add_argument("--phone")
    acc.add_argument("--machine")
    acc.add_argument("--ip")
    acc.add_argument("--os")
    acc.add_argument("--type", dest="contact_type")
    exp = sub.add_parser("export", help="write customer_devices CSV")
    exp.add_argument("-o", "--out", default="dolphin_pod_export.csv")
    rev = sub.add_parser("revoke", help="revoke a pending invite")
    rev.add_argument("--email")
    rev.add_argument("--token")
    rev.add_argument("--id", type=int, dest="invite_id")
    who_p = sub.add_parser("who", help="lookup a person or machine")
    who_p.add_argument("query")
    st = sub.add_parser("set-type", help="tag an existing person")
    st.add_argument("--type", dest="contact_type", required=True)
    st.add_argument("--email")
    st.add_argument("--name")
    sub.add_parser("types", help="print contact type slugs")
    sub.add_parser("rolodex", help="write local Rolladex HTML")
    sub.add_parser("outreach", help="print outreach table and write HTML/CSV")
    rp = sub.add_parser("reply", help="fill who replied / times on a contact")
    rp.add_argument("--email")
    rp.add_argument("--name")
    rp.add_argument("--who", dest="who_replied")
    rp.add_argument("--replied-at")
    rp.add_argument("--sent-at")
    rp.add_argument("--channel")
    rp.add_argument("--time-to-reply")
    rp.add_argument("--follow-up")
    rp.add_argument("--outcome")
    rp.add_argument("--notes")
    args = p.parse_args()
    if args.cmd == "types":
        list_types()
        return
    if args.cmd == "rolodex":
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from rolodex import main as write_rolodex
        write_rolodex()
        return
    if args.cmd == "outreach":
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from outreach import main as write_outreach
        conn = connect()
        list_outreach(conn)
        write_outreach()
        return
    if args.cmd == "reply":
        conn = connect()
        oid = set_reply(
            conn, args.email, args.name, args.who_replied, args.replied_at,
            args.sent_at, args.channel, args.time_to_reply, args.follow_up,
            args.outcome, args.notes,
        )
        conn.commit()
        print(f"outreach_id={oid}")
        list_outreach(conn)
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from outreach import main as write_outreach
        write_outreach()
        return
    conn = connect()
    if args.cmd == "list":
        list_all(conn, args.contact_type)
        return
    if args.cmd == "invites":
        list_invites(conn)
        return
    if args.cmd == "export":
        export_csv(conn, args.out)
        return
    if args.cmd == "revoke":
        n = revoke_invite(conn, args.email, args.token, args.invite_id)
        conn.commit()
        print(f"revoked {n} invite(s)")
        list_invites(conn)
        return
    if args.cmd == "who":
        who(conn, args.query)
        return
    if args.cmd == "set-type":
        n = set_type(conn, args.contact_type, args.email, args.name)
        conn.commit()
        print(f"updated {n}")
        list_all(conn)
        return
    if args.cmd == "accept":
        cid = accept_invite(
            conn, args.email, args.token, args.phone, args.machine, args.ip, args.os, args.contact_type
        )
        conn.commit()
        print(f"accepted -> customer_id={cid}")
        list_all(conn)
        return
    if args.cmd == "invite":
        token = add_invite(conn, args.email, args.first, args.last, args.role, args.contact_type)
        conn.commit()
        print(f"pending invite for {args.email} type={normalize_type(args.contact_type) or '-'}")
        print(f"token={token}")
        print("They still must accept a Tailscale invite in the admin console.")
        list_invites(conn)
        return
    cid = upsert_customer(
        conn, args.first, args.last, args.email, args.phone, args.display, args.role,
        notes=getattr(args, "notes", None), contact_type=args.contact_type,
        org=getattr(args, "org", None), title=getattr(args, "title", None),
    )
    if args.machine:
        upsert_device(conn, cid, args.machine, args.ip, os=args.os)
    conn.commit()
    print(f"customer_id={cid} type={normalize_type(args.contact_type) or '-'}")
    list_all(conn)


if __name__ == "__main__":
    main()
