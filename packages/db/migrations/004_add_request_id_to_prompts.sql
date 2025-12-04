-- Migration: Feedback System Database Migration
-- Date: 2025-12-04
-- Purpose: Migrate feedback system from CSV to SQLite database

-- Step 1: Add request_id to prompts table (for feedback linkage)
-- SQLite doesn't support IF NOT EXISTS in ALTER TABLE, so check if column exists first
-- If migration already ran, this will fail silently
ALTER TABLE prompts ADD COLUMN request_id TEXT;

-- Step 2: Create user_feedback table
CREATE TABLE IF NOT EXISTS user_feedback (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    prompt_id TEXT NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    user_choice TEXT NOT NULL CHECK (user_choice IN ('original', 'single', 'multi')),
    judge_winner TEXT NOT NULL,
    agent_winner TEXT NOT NULL,
    judge_correct INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for user_feedback table
CREATE INDEX IF NOT EXISTS idx_user_feedback_request_id ON user_feedback(request_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON user_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_prompt_id ON user_feedback(prompt_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_agent_winner ON user_feedback(agent_winner);

-- Create index for prompts request_id (if not exists)
CREATE INDEX IF NOT EXISTS idx_prompts_request_id ON prompts(request_id);

