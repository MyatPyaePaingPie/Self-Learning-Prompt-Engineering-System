-- 002_add_security_inputs.sql
CREATE TABLE security_inputs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT,
  input_text TEXT NOT NULL,
  risk_score NUMERIC NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
  label TEXT NOT NULL CHECK (label IN ('safe', 'low-risk', 'medium-risk', 'high-risk', 'blocked')),
  is_blocked BOOLEAN NOT NULL DEFAULT FALSE,
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_security_inputs_created_at ON security_inputs(created_at DESC);
CREATE INDEX idx_security_inputs_label ON security_inputs(label);
CREATE INDEX idx_security_inputs_blocked ON security_inputs(is_blocked);
CREATE INDEX idx_security_inputs_risk_score ON security_inputs(risk_score DESC);

