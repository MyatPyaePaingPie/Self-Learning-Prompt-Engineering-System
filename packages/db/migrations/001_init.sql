-- 001_init_sqlite.sql - SQLite compatible version
CREATE TABLE prompts (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  original_text TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prompt_versions (
  id TEXT PRIMARY KEY,
  prompt_id TEXT NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
  version_no INTEGER NOT NULL,
  text TEXT NOT NULL,
  explanation TEXT NOT NULL,
  source TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (prompt_id, version_no)
);

CREATE TABLE judge_scores (
  id TEXT PRIMARY KEY,
  prompt_version_id TEXT NOT NULL REFERENCES prompt_versions(id) ON DELETE CASCADE,
  clarity REAL NOT NULL CHECK (clarity BETWEEN 0 AND 10),
  specificity REAL NOT NULL CHECK (specificity BETWEEN 0 AND 10),
  actionability REAL NOT NULL CHECK (actionability BETWEEN 0 AND 10),
  structure REAL NOT NULL CHECK (structure BETWEEN 0 AND 10),
  context_use REAL NOT NULL CHECK (context_use BETWEEN 0 AND 10),
  total REAL NOT NULL,
  feedback TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE best_heads (
  prompt_id TEXT PRIMARY KEY REFERENCES prompts(id) ON DELETE CASCADE,
  prompt_version_id TEXT NOT NULL REFERENCES prompt_versions(id) ON DELETE CASCADE,
  score REAL NOT NULL,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_prompt_versions_prompt ON prompt_versions(prompt_id);
CREATE INDEX idx_judge_scores_pv ON judge_scores(prompt_version_id);