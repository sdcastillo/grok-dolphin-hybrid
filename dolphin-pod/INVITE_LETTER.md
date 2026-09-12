# DOLPHIN POD invite letter (copy/paste)

Private mesh. Consent only. No location tracking.

Subject: Invite to DOLPHIN POD (Tailscale)

Hi FIRST,

I’m standing up a small private network — DOLPHIN POD — for teammates who want in on purpose.

What it is:
- A Tailscale mesh so we can reach each other’s machines by name
- A registry of people and devices you choose to add (name, email, phone if you want, Tailscale hostname/IP)
- Not a public map. Exact location is not stored and is not posted.

How to join:
1. Accept the Tailscale invite I’ll send from the admin console (marlin-pollux.ts.net).
2. Reply with the hostname of the machine you want registered, and whether you want a phone number on file.
3. I’ll add you with:

```
python3 register.py invite --email YOU@EMAIL --first FIRST --last LAST --role dev
python3 register.py accept --email YOU@EMAIL --machine YOUR-HOSTNAME
```

You can leave anytime. Unregistered devices (including other people’s phones) stay off the list.

— Sam
