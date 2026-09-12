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

## More commands

```bash
python3 register.py invite --email them@example.com --first NAME --last NAME --role dev
python3 register.py accept --email them@example.com --machine hostname
python3 register.py who NAME
python3 register.py revoke --email them@example.com
python3 register.py export -o export.csv
bash status.sh
```

## Contact types

```bash
python3 register.py types
python3 register.py add --first NAME --last NAME --email a@b.c --type business
python3 register.py set-type --name NAME --type researcher
python3 register.py list --type client
```
