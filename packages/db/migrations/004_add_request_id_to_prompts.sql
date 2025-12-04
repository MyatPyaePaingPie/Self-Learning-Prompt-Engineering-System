-- Migration: Add request_id to prompts table
-- Date: 2025-12-04
-- Purpose: Track request_id for feedback linkage

ALTER TABLE prompts ADD COLUMN IF NOT EXISTS request_id VARCHAR;

-- Create index for fast lookups by request_id
CREATE INDEX IF NOT EXISTS idx_prompts_request_id ON prompts(request_id);

