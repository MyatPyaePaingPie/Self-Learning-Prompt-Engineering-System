-- 001_init.sql
CREATE TABLE prompts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT,
  original_text TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE prompt_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prompt_id UUID NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
  version_no INT NOT NULL,               -- 0 = original, 1..n = rewrites
  text TEXT NOT NULL,
  explanation JSONB NOT NULL,            -- {bullets: [...], diffs: [...]} 
  source TEXT NOT NULL,                  -- 'original' | 'engine/vX'
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (prompt_id, version_no)
);

CREATE TABLE judge_scores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prompt_version_id UUID NOT NULL REFERENCES prompt_versions(id) ON DELETE CASCADE,
  clarity NUMERIC NOT NULL CHECK (clarity BETWEEN 0 AND 10),
  specificity NUMERIC NOT NULL CHECK (specificity BETWEEN 0 AND 10),
  actionability NUMERIC NOT NULL CHECK (actionability BETWEEN 0 AND 10),
  structure NUMERIC NOT NULL CHECK (structure BETWEEN 0 AND 10),
  context_use NUMERIC NOT NULL CHECK (context_use BETWEEN 0 AND 10),
  total NUMERIC GENERATED ALWAYS AS (clarity+specificity+actionability+structure+context_use) STORED,
  feedback JSONB NOT NULL,               -- {pros:[], cons:[], summary:""}
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE best_heads (
  prompt_id UUID PRIMARY KEY REFERENCES prompts(id) ON DELETE CASCADE,
  prompt_version_id UUID NOT NULL REFERENCES prompt_versions(id) ON DELETE CASCADE,
  score NUMERIC NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_prompt_versions_prompt ON prompt_versions(prompt_id);
CREATE INDEX idx_judge_scores_pv ON judge_scores(prompt_version_id);