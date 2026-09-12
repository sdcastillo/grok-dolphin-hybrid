# DOLPHIN POD registry

SQLite registry for people and Tailscale devices on the DOLPHIN POD network.

## Schema

- `customers` — first, last, name, email, phone, role
- `devices` — tailscale_name, tailscale_ip, os, last_seen (FK to customer)
- `customer_devices` — flat view for exports

Location is **not** stored here. Exact pins stay off posts; no tracking of other people’s phones.

## Commands

```bash
cd dolphin-pod
python3 register.py list
python3 register.py add --first Ada --last Lovelace --email ada@example.com --phone +1-555-0100 \
  --machine ada-laptop --ip 100.x.x.x --os linux --role dev
```

Database file: `dolphin_pod.sqlite` (gitignored). Recreate with:

```bash
sqlite3 dolphin_pod.sqlite < schema.sql
python3 register.py add --first ...
```
