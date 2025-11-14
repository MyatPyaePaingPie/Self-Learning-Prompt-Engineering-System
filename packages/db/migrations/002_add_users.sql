-- 002_add_users.sql - Add User table (SQLite compatible)

-- Create users table
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_login TEXT
);

-- Create index on username for fast login lookups
CREATE INDEX idx_users_username ON users(username);