#!/usr/bin/env python3
"""Write a local-only Rolladex. Cards by contact type. No location."""
from __future__ import annotations

import html
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
DB = DIR / "dolphin_pod.sqlite"
OUT = DIR / "rolodex.html"

ORDER = ["self", "business", "client", "manager", "researcher", "romantic", ""]
LABELS = {
    "self": "You",
    "business": "Business",
    "client": "Client",
    "manager": "Boss / manager",
    "researcher": "Student / researcher",
    "romantic": "Romantic (private)",
    "": "Unfiled",
}


def esc(v) -> str:
    return html.escape("" if v is None else str(v))


def people():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT id, first_name, last_name,
                  COALESCE(display_name, first_name || ' ' || last_name) AS name,
                  email, phone, role, contact_type, org, title, notes
           FROM customers ORDER BY last_name, first_name"""
    ).fetchall()
    conn.close()
    return rows


def card(c) -> str:
    letter = (c["last_name"] or c["name"] or "?")[:1].upper()
    org = esc(c["org"])
    title = esc(c["title"])
    sub = " · ".join(x for x in (title, org) if x)
    phone = esc(c["phone"])
    email = esc(c["email"])
    notes = esc(c["notes"])
    bits = [
        "<article class='card' data-type='{t}' data-letter='{L}' data-q='{q}'>".format(
            t=esc(c["contact_type"] or ""),
            L=esc(letter),
            q=esc(" ".join(filter(None, [c["name"], c["email"], c["phone"], c["org"], c["title"], c["notes"]])).lower()),
        ),
        f"<div class='tab'>{esc(letter)}</div>",
        f"<h3>{esc(c['name'])}</h3>",
    ]
    if sub:
        bits.append(f"<p class='sub'>{sub}</p>")
    bits.append(f"<p class='type'>{esc(LABELS.get(c['contact_type'] or '', c['contact_type'] or 'Unfiled'))}</p>")
    if email:
        bits.append(f"<p class='line'><span>email</span> {email}</p>")
    if phone:
        bits.append(f"<p class='line'><span>phone</span> {phone}</p>")
    if notes:
        bits.append(f"<p class='notes'>{notes}</p>")
    bits.append("</article>")
    return "\n".join(bits)


def main() -> None:
    rows = people()
    grouped: dict[str, list] = defaultdict(list)
    for r in rows:
        grouped[r["contact_type"] or ""].append(r)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    filters = "".join(
        f"<button type='button' data-filter='{esc(k)}'>{esc(LABELS[k])} <em>{len(grouped.get(k, []))}</em></button>"
        for k in ORDER
        if k in grouped or k == ""
    )
    # always show typed buckets even if empty
    filters = "".join(
        f"<button type='button' data-filter='{esc(k)}'>{esc(LABELS[k])} <em>{len(grouped.get(k, []))}</em></button>"
        for k in ORDER
    )
    cards = []
    for k in ORDER:
        for r in grouped.get(k, []):
            cards.append(card(r))
    # any unexpected types
    for k, rs in grouped.items():
        if k not in ORDER:
            for r in rs:
                cards.append(card(r))

    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ROLLADEX</title>
<style>
:root {{ --ink:#1b140c; --paper:#f4e7c8; --card:#fff6df; --tab:#c45c26; --rule:#d6c4a0; --mute:#7a6848; }}
html,body {{ margin:0; background:#2a2116; color:var(--ink); font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif; }}
header {{ padding:1.4rem 1.6rem .6rem; color:var(--paper); }}
header h1 {{ margin:0; letter-spacing:.22em; font-size:1.15rem; }}
header p {{ margin:.35rem 0 0; color:#cbb892; font-size:.9rem; }}
.bar {{ display:flex; flex-wrap:wrap; gap:.4rem; padding:0 1.6rem 1rem; }}
.bar button {{ background:#3a2e20; color:var(--paper); border:1px solid #5a4630; border-radius:999px; padding:.35rem .75rem; font:inherit; cursor:pointer; }}
.bar button.on, .bar button:hover {{ background:var(--tab); border-color:var(--tab); color:#fff6df; }}
.bar em {{ font-style:normal; opacity:.75; }}
input[type=search] {{ margin:0 1.6rem 1.2rem; width:calc(100% - 3.2rem); max-width:28rem; padding:.5rem .7rem; border:1px solid #5a4630; background:#3a2e20; color:var(--paper); font:inherit; border-radius:6px; }}
.deck {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:1rem; padding:0 1.6rem 2.4rem; }}
.card {{ background:linear-gradient(#fffaf0,var(--card)); border:1px solid var(--rule); border-radius:4px 14px 8px 8px; padding:1.1rem 1rem .9rem; position:relative; box-shadow:3px 4px 0 #1a140c55; min-height:10rem; }}
.card.hid {{ display:none; }}
.tab {{ position:absolute; top:-1px; right:1.1rem; background:var(--tab); color:#fff6df; padding:.15rem .55rem; border-radius:0 0 6px 6px; font-weight:700; letter-spacing:.08em; }}
h3 {{ margin:.2rem 1.8rem 0 0; font-size:1.2rem; }}
.sub,.type,.line,.notes {{ margin:.25rem 0 0; }}
.sub {{ color:#5c4a2e; }}
.type {{ font-size:.8rem; letter-spacing:.08em; text-transform:uppercase; color:var(--tab); }}
.line span {{ display:inline-block; width:3.4rem; color:var(--mute); font-size:.8rem; text-transform:uppercase; letter-spacing:.06em; }}
.notes {{ color:#5c4a2e; font-size:.92rem; }}
footer {{ color:#cbb892; padding:0 1.6rem 2rem; font-size:.85rem; }}
</style>
</head>
<body>
<header>
  <h1>ROLLADEX</h1>
  <p>{esc(now)} · {len(rows)} cards · local only · no location</p>
</header>
<div class="bar">
  <button type="button" class="on" data-filter="*">All <em>{len(rows)}</em></button>
  {filters}
</div>
<input type="search" id="q" placeholder="Search name, email, org…">
<section class="deck">
{chr(10).join(cards) if cards else "<p style='color:#cbb892'>Empty. Add someone with register.py add --type …</p>"}
</section>
<footer>Private file. Romantic labels stay here. Do not post. Unregistered people are not invented.</footer>
<script>
const cards=[...document.querySelectorAll('.card')];
let type='*';
function apply(){{
  const q=(document.getElementById('q').value||'').toLowerCase();
  cards.forEach(c=>{{
    const okT=type==='*'||c.dataset.type===type;
    const okQ=!q||(c.dataset.q||'').includes(q);
    c.classList.toggle('hid',!(okT&&okQ));
  }});
}}
document.querySelector('.bar').addEventListener('click',e=>{{
  const b=e.target.closest('button'); if(!b) return;
  document.querySelectorAll('.bar button').forEach(x=>x.classList.toggle('on',x===b));
  type=b.dataset.filter; apply();
}});
document.getElementById('q').addEventListener('input',apply);
</script>
</body>
</html>
"""
    OUT.write_text(html_out)
    print(f"wrote {OUT} ({len(rows)} cards)")


if __name__ == "__main__":
    main()
