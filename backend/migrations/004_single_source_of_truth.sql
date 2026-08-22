-- 004: single source of truth for asset metadata
--
-- asset_embeddings previously duplicated the full asset metadata dict
-- (owner, description, file_url, ...) alongside the vector. Two stores
-- drifted silently when one write failed. The `assets` table is now THE
-- authoritative store; this table holds only the fingerprint.
--
-- Apply order: after 000-002.

-- 1. Remove orphaned embeddings (no matching assets row — legacy half-writes)
delete from asset_embeddings e
where not exists (select 1 from assets a where a.asset_id = e.id);

-- 2. match_assets now joins to assets so similarity search returns the
--    authoritative phash (and can never return an orphaned embedding).
--    The return type changes (metadata -> phash), so the old signature
--    must be dropped first — CREATE OR REPLACE cannot change OUT params.
drop function if exists match_assets(vector, integer, double precision);

create or replace function match_assets(
  query_embedding vector(512),
  match_count int,
  similarity_threshold float
)
returns table (
  id text,
  phash text,
  similarity float
)
language sql stable as $$
  select
    e.id,
    a.phash,
    1 - (e.embedding <=> query_embedding) as similarity
  from asset_embeddings e
  join assets a on a.asset_id = e.id
  where 1 - (e.embedding <=> query_embedding) >= similarity_threshold
  order by e.embedding <=> query_embedding
  limit match_count;
$$;

-- 3. Drop the duplicated columns.
alter table asset_embeddings
  drop column if exists metadata,
  drop column if exists document;
