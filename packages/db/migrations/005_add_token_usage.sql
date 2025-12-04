-- Migration: Token Usage Tracking
-- Date: 2025-12-04
-- Purpose: Track token usage and LLM model history for prompt versions

CREATE TABLE IF NOT EXISTS token_usage (
    id TEXT PRIMARY KEY,
    prompt_version_id TEXT NOT NULL REFERENCES prompt_versions(id) ON DELETE CASCADE,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    model TEXT NOT NULL,
    cost_usd REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_token_usage_prompt_version_id ON token_usage(prompt_version_id);
CREATE INDEX IF NOT EXISTS idx_token_usage_model ON token_usage(model);
CREATE INDEX IF NOT EXISTS idx_token_usage_created_at ON token_usage(created_at);

