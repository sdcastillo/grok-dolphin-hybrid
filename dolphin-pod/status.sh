#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
echo "=== DOLPHIN POD ==="
python3 "$DIR/register.py" list
echo
echo "=== invites ==="
python3 "$DIR/register.py" invites
echo
if command -v tailscale >/dev/null; then
  echo "=== tailscale (humans/machines, no funnel) ==="
  tailscale status 2>/dev/null | grep -v funnel | grep -v '^$' | grep -v Health | grep -v overwritten | grep -v 'Funnel on' | grep -v marlin-pollux.ts.net || true
fi
python3 "$DIR/status_html.py"
python3 "$DIR/rolodex.py"
python3 "$DIR/outreach.py"
echo
echo "status page: $DIR/status.html"
echo "rolodex: $DIR/rolodex.html"
echo "outreach: $DIR/outreach.html"
