#!/usr/bin/env python3
"""Write outreach table (HTML + CSV) with empty reply columns to fill later."""
from __future__ import annotations

import csv
import html
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
DB = DIR / "dolphin_pod.sqlite"
HTML = DIR / "outreach.html"
CSV = DIR / "outreach.csv"

COLS = [
    "name",
    "type",
    "email",
    "phone",
    "org",
    "title",
    "channel",
    "sent_at",
    "who_replied",
    "replied_at",
    "time_to_reply",
    "follow_up_at",
    "outcome",
    "notes",
]


def esc(v) -> str:
    return html.escape("" if v is None else str(v))


def cell(v) -> str:
    s = "" if v is None else str(v)
    return s


def rows():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    data = conn.execute(
        """SELECT
             COALESCE(c.display_name, c.first_name || ' ' || c.last_name) AS name,
             c.contact_type AS type,
             c.email, c.phone, c.org, c.title,
             o.channel, o.sent_at, o.who_replied, o.replied_at,
             o.time_to_reply, o.follow_up_at, o.outcome, o.notes
           FROM customers c
           LEFT JOIN outreach o ON o.customer_id = c.id
           ORDER BY c.contact_type, c.last_name, c.first_name, o.id"""
    ).fetchall()
    conn.close()
    return data


def main() -> None:
    data = rows()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    with CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for r in data:
            w.writerow([cell(r[c]) for c in COLS])
        if not data:
            w.writerow([""] * len(COLS))
    print(f"wrote {CSV} ({len(data)} rows)")

    head = "".join(f"<th>{esc(c.replace('_', ' '))}</th>" for c in COLS)
    body = []
    for r in data:
        tds = []
        for c in COLS:
            val = cell(r[c])
            empty = " empty" if val == "" else ""
            tds.append(f"<td class='{c}{empty}'>{esc(val)}</td>")
        body.append("<tr>" + "".join(tds) + "</tr>")
    if not body:
        body.append("<tr>" + "".join(f"<td class='empty'></td>" for _ in COLS) + "</tr>")

    HTML.write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ROLLADEX outreach</title>
<style>
body{{margin:0;background:#2a2116;color:#f4e7c8;font-family:"Iowan Old Style",Palatino,Georgia,serif;}}
header{{padding:1.4rem 1.6rem .7rem;}}
h1{{margin:0;letter-spacing:.18em;font-size:1.1rem;}}
p{{margin:.4rem 0 0;color:#cbb892;font-size:.9rem;}}
.wrap{{padding:0 1.6rem 2rem;overflow:auto;}}
table{{border-collapse:collapse;min-width:1200px;background:#fff6df;color:#1b140c;}}
th,td{{border:1px solid #d6c4a0;padding:.45rem .55rem;text-align:left;font-size:.92rem;white-space:nowrap;}}
th{{background:#c45c26;color:#fff6df;font-weight:600;}}
td.empty{{background:#fffaf0;min-width:7rem;height:1.6rem;}}
td.who_replied,td.time_to_reply,td.replied_at,td.sent_at,td.follow_up_at,td.channel,td.outcome,td.notes{{min-width:8rem;}}
tr:nth-child(even) td{{background:#f7ead0;}}
tr:nth-child(even) td.empty{{background:#fff6df;}}
a{{color:#f4e7c8;}}
</style>
</head>
<body>
<header>
  <h1>ROLLADEX · outreach</h1>
  <p>{esc(now)} · {len(data)} row(s) · empty cells are for you to fill later · <a href="rolodex.html">cards</a></p>
</header>
<div class="wrap">
<table>
<thead><tr>{head}</tr></thead>
<tbody>
{chr(10).join(body)}
</tbody>
</table>
</div>
</body>
</html>
"""
    )
    print(f"wrote {HTML}")


if __name__ == "__main__":
    main()
