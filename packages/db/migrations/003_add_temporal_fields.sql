-- Migration: Add temporal fields to prompt_versions table
-- Week 12: Temporal Prompt Learning & Causal Analysis
-- Date: 2025-12-03

-- Add parent_version_id for version chains
ALTER TABLE prompt_versions ADD COLUMN parent_version_id TEXT;
ALTER TABLE prompt_versions ADD FOREIGN KEY (parent_version_id) REFERENCES prompt_versions(id) ON DELETE SET NULL;

-- Add change_type for categorizing prompt changes
ALTER TABLE prompt_versions ADD COLUMN change_type TEXT DEFAULT 'other';

-- Add change_magnitude for quantifying edit distance
ALTER TABLE prompt_versions ADD COLUMN change_magnitude REAL DEFAULT 0.0;

-- Create index on parent_version_id for efficient version chain queries
CREATE INDEX idx_prompt_versions_parent ON prompt_versions(parent_version_id);

-- Create index on created_at for temporal queries
CREATE INDEX idx_prompt_versions_created_at ON prompt_versions(created_at);

