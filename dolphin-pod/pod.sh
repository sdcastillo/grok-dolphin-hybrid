#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
cmd="${1:-serve}"
case "$cmd" in
  migrate)
    python3 migrate_contact_type.py
    python3 migrate_rolodex.py
    python3 migrate_outreach.py
    ;;
  pages)
    python3 status_html.py
    python3 rolodex.py
    python3 outreach.py
    ;;
  serve)
    python3 migrate_contact_type.py
    python3 migrate_rolodex.py
    python3 migrate_outreach.py
    python3 status_html.py
    python3 rolodex.py
    python3 outreach.py
    exec python3 serve.py
    ;;
  status)
    bash status.sh
    ;;
  *)
    echo "usage: $0 migrate|pages|serve|status"
    exit 1
    ;;
esac
