CREATE TABLE IF NOT EXISTS invites (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  email       TEXT NOT NULL,
  first_name  TEXT,
  last_name   TEXT,
  role        TEXT DEFAULT 'dev',
  token       TEXT UNIQUE,
  status      TEXT NOT NULL DEFAULT 'pending', -- pending | accepted | revoked
  created_at  TEXT NOT NULL DEFAULT (datetime('now')),
  accepted_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_invites_email ON invites(email);
CREATE INDEX IF NOT EXISTS idx_invites_status ON invites(status);
