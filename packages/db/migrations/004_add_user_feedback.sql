-- Migration: Add user_feedback table
-- Date: 2025-12-04
-- Purpose: Migrate feedback system from CSV to database

CREATE TABLE IF NOT EXISTS user_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id VARCHAR NOT NULL,
    user_id VARCHAR NOT NULL,
    prompt_id UUID NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    user_choice VARCHAR NOT NULL CHECK (user_choice IN ('original', 'single', 'multi')),
    judge_winner VARCHAR NOT NULL,
    agent_winner VARCHAR NOT NULL,
    judge_correct BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create index for fast lookups by request_id
CREATE INDEX IF NOT EXISTS idx_user_feedback_request_id ON user_feedback(request_id);

-- Create index for user-specific queries
CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON user_feedback(user_id);

-- Create index for prompt-specific queries
CREATE INDEX IF NOT EXISTS idx_user_feedback_prompt_id ON user_feedback(prompt_id);

-- Create index for agent effectiveness queries
CREATE INDEX IF NOT EXISTS idx_user_feedback_agent_winner ON user_feedback(agent_winner);

