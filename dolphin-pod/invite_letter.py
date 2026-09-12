#!/usr/bin/env python3
"""Fill the reusable invite letter. Does not send email."""
from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent / "INVITE_LETTER.md"


def main() -> None:
    p = argparse.ArgumentParser(description="Fill DOLPHIN POD invite letter (no send)")
    p.add_argument("--first", required=True)
    p.add_argument("--last", required=True)
    p.add_argument("--email", required=True)
    p.add_argument("--role", default="dev")
    p.add_argument("-o", "--out")
    args = p.parse_args()
    text = TEMPLATE.read_text()
    text = text.replace("FIRST", args.first).replace("LAST", args.last)
    text = text.replace("YOU@EMAIL", args.email).replace("YOUR-HOSTNAME", "HOSTNAME")
    text = text.replace("--role dev", f"--role {args.role}")
    out = Path(args.out) if args.out else Path(f"invite_{args.first.lower()}_{args.last.lower()}.md")
    out.write_text(text)
    print(f"wrote {out} (not sent)")


if __name__ == "__main__":
    main()
