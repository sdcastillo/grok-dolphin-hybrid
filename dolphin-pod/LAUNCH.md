# DOLPHIN POD launch

Private Tailscale network + customer/device registry. Not a public GPS map.

## What’s live

- Registry: `dolphin_pod.sqlite` (`customers`, `devices`, `invites`)
- CLI: `register.py add|list`
- Sync: `sync_tailscale.py` — refreshes **already registered** machines only
- Hybrid model: https://huggingface.co/Samzzzed/dolphin-mistral-7b
- Install: `bash install.sh` in repo root
- Tailnet: `marlin-pollux.ts.net`

## Add a teammate (consent)

1. Invite them in the Tailscale admin console (they accept).
2. Register them here — don’t invent phones:

```bash
python3 register.py invite --email them@example.com --first NAME --last NAME --role dev
python3 register.py add --first NAME --last NAME --email them@example.com --role dev \
  --machine their-hostname --ip 100.x.x.x
```

3. Run `python3 sync_tailscale.py` on Jarvis to refresh online/IP.

## Rules

- Exact location stays off posts and off this database.
- Do not auto-enroll unknown Tailscale nodes.
- Andy / other people’s phones are not tracked unless they register themselves.

## Accept + export

```bash
python3 register.py accept --email them@example.com --machine their-hostname --ip 100.x.x.x
python3 register.py export -o ~/DOLPHIN_POD/export.csv
```

## Lookup / revoke / local page

```bash
python3 register.py who Sam
python3 register.py revoke --email them@example.com
bash status.sh   # also writes status.html (local, no location)
```

## Invite letter (no send)

Copy `INVITE_LETTER.md`, or fill a local draft:

```bash
python3 invite_letter.py --first NAME --last NAME --email them@example.com -o ~/DOLPHIN_POD/invite_draft.md
```

Then invite them in the Tailscale admin console. Do not auto-enroll devices.

## Contact types

`role` is mesh privilege (member/dev/admin). `contact_type` is the relationship bucket:

| slug | meaning |
|---|---|
| self | you |
| business | business |
| client | client |
| manager | future boss / manager |
| researcher | student / researcher |
| romantic | romantic / spouse potential (private) |

```bash
python3 register.py types
python3 register.py add --first NAME --last NAME --email them@example.com --type client
python3 register.py set-type --email them@example.com --type manager
python3 register.py list --type business
```

Romantic is a private label only. Do not post it. Do not infer it from a name.

## Rolladex

Local card file. Same people as the registry. No street address.

```bash
python3 register.py add --first NAME --last NAME --email a@b.c --phone 555 --type client --org Acme --title Analyst
python3 register.py rolodex
# open ~/DOLPHIN_POD/rolodex.html
```

## Outreach table

Empty columns to fill later: channel, sent_at, who_replied, replied_at, time_to_reply, follow_up_at, outcome, notes.

```bash
python3 migrate_outreach.py
python3 register.py outreach          # writes outreach.html + outreach.csv
python3 register.py reply --email them@example.com --who NAME --replied-at "2026-09-18 16:00" --time-to-reply "2d"
```

Open `outreach.html` or `outreach.csv`. Home copy on Polar: `~/DOLPHIN_POD/`.
