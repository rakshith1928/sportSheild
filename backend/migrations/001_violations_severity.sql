-- 001: persist violation severity
--
-- The backend now writes a `severity` column at insert time
-- (services/database.py :: severity_from_similarity). This migration must
-- be applied BEFORE deploying that change, otherwise violation inserts
-- will fail against the live schema.
--
-- Thresholds (must stay in sync with severity_from_similarity):
--   clip_similarity > 0.9  -> 'high'
--   clip_similarity > 0.75 -> 'medium'
--   else                   -> 'low'

ALTER TABLE violations
    ADD COLUMN IF NOT EXISTS severity text;

UPDATE violations
SET severity = CASE
    WHEN clip_similarity > 0.9 THEN 'high'
    WHEN clip_similarity > 0.75 THEN 'medium'
    ELSE 'low'
END
WHERE severity IS NULL;

CREATE INDEX IF NOT EXISTS idx_violations_severity ON violations (severity);
