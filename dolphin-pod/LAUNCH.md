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
