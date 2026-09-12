-- DOLPHIN POD registry
-- customers = people; devices = Tailscale nodes (one customer, many machines)

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS customers (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name    TEXT NOT NULL,
  last_name     TEXT NOT NULL,
  display_name  TEXT,
  email         TEXT UNIQUE,
  phone         TEXT,
  role          TEXT DEFAULT 'member', -- member | dev | admin | guest
  contact_type  TEXT, -- self | business | client | manager | researcher | romantic
  notes         TEXT,
  created_at    TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS devices (
  id                   INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id          INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  tailscale_name       TEXT NOT NULL,
  tailscale_ip         TEXT,
  tailscale_ipv6       TEXT,
  os                   TEXT,
  online               INTEGER DEFAULT 0,
  last_seen            TEXT,
  notes                TEXT,
  created_at           TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at           TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (tailscale_name)
);

CREATE INDEX IF NOT EXISTS idx_devices_customer ON devices(customer_id);
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_type ON customers(contact_type);

CREATE VIEW IF NOT EXISTS customer_devices AS
SELECT
  c.id AS customer_id,
  c.first_name,
  c.last_name,
  COALESCE(c.display_name, c.first_name || ' ' || c.last_name) AS name,
  c.email,
  c.phone,
  c.role,
  c.contact_type,
  d.id AS device_id,
  d.tailscale_name,
  d.tailscale_ip,
  d.os,
  d.online,
  d.last_seen
FROM customers c
LEFT JOIN devices d ON d.customer_id = c.id;
CREATE TABLE IF NOT EXISTS invites (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  email       TEXT NOT NULL,
  first_name  TEXT,
  last_name   TEXT,
  role        TEXT DEFAULT 'dev',
  contact_type TEXT,
  token       TEXT UNIQUE,
  status      TEXT NOT NULL DEFAULT 'pending', -- pending | accepted | revoked
  created_at  TEXT NOT NULL DEFAULT (datetime('now')),
  accepted_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_invites_email ON invites(email);
CREATE INDEX IF NOT EXISTS idx_invites_status ON invites(status);
