-- 000: baseline schema for SportShield AI
--
-- Reconstructed from actual application usage (services/database.py,
-- services/vector_store.py) because no migrations existed before this
-- point — tables were created manually in Supabase.
--
-- Apply order: 000_baseline_schema.sql -> 001_violations_severity.sql
-- (001 is idempotent and required: the backend writes violations.severity).
--
-- NOTE ON RLS: the backend connects with the service-role key, which
-- bypasses RLS by design; tenancy is enforced at the API layer
-- (owner checks + PostgREST inner-join scoping). If you ever expose these
-- tables to client-side Supabase SDKs, write and test RLS policies first.

create extension if not exists vector;

-- ─────────────────────────────────────────────────────────────
-- Assets: user-uploaded media metadata (files live in Storage)
-- ─────────────────────────────────────────────────────────────
create table if not exists assets (
  asset_id          text primary key,
  filename          text not null,
  original_filename text,
  sport             text not null,
  team              text not null,
  event             text default '',
  description       text default '',
  owner             uuid not null,            -- auth.users.id
  date              text default '',
  file_url          text,
  content_type      text,
  file_size_mb      double precision,
  phash             text,
  fingerprinted_at  timestamptz,
  created_at        timestamptz default now()
);

create index if not exists idx_assets_owner on assets (owner);

-- ─────────────────────────────────────────────────────────────
-- Scans: one row per web-scan run against an asset
-- ─────────────────────────────────────────────────────────────
create table if not exists scans (
  id               uuid primary key default gen_random_uuid(),
  asset_id         text not null references assets (asset_id) on delete cascade,
  status           text not null default 'scanning',  -- scanning|completed|failed
  query_used       text default '',
  total_scanned    int default 0,
  violations_found int default 0,
  errors           jsonb default '[]',
  started_at       timestamptz default now(),
  completed_at     timestamptz
);

create index if not exists idx_scans_asset on scans (asset_id);
create index if not exists idx_scans_started on scans (started_at desc);

-- ─────────────────────────────────────────────────────────────
-- Violations: detected infringing uses of an asset
-- ─────────────────────────────────────────────────────────────
create table if not exists violations (
  id              bigserial primary key,
  asset_id        text references assets (asset_id) on delete cascade,
  scan_id         uuid references scans (id) on delete set null,
  image_url       text not null,
  page_url        text not null,
  title           text default 'Unknown',
  clip_similarity double precision,
  phash_distance  int,
  is_likely_copy  boolean default false,
  severity        text,                     -- high|medium|low (see 001)
  detected_at     timestamptz
);

create index if not exists idx_violations_asset on violations (asset_id);
create index if not exists idx_violations_detected on violations (detected_at desc);

-- ─────────────────────────────────────────────────────────────
-- Reports: generated PDF takedown reports
-- ─────────────────────────────────────────────────────────────
create table if not exists reports (
  report_id           text primary key,     -- 8 uppercase hex chars
  asset_id            text not null references assets (asset_id) on delete cascade,
  violations_analyzed int default 0,
  file_path           text,
  download_url        text,
  generated_at        timestamptz default now()
);

create index if not exists idx_reports_asset on reports (asset_id);
create index if not exists idx_reports_generated on reports (generated_at desc);

-- ─────────────────────────────────────────────────────────────
-- pgvector stores (mirrors services/vector_store.py docstring)
-- ─────────────────────────────────────────────────────────────
create table if not exists asset_embeddings (
  id         text primary key,
  embedding  vector(512),
  metadata   jsonb,
  document   text,
  created_at timestamptz default now()
);
create index on asset_embeddings using ivfflat (embedding vector_cosine_ops);

create table if not exists rag_documents (
  id         uuid primary key default gen_random_uuid(),
  content    text,
  metadata   jsonb,
  embedding  vector(384),
  created_at timestamptz default now()
);
create index on rag_documents using ivfflat (embedding vector_cosine_ops);

-- RPC for cosine similarity search (asset fingerprints)
create or replace function match_assets(
  query_embedding vector(512),
  match_count int,
  similarity_threshold float
)
returns table (
  id text,
  metadata jsonb,
  similarity float
)
language sql stable as $$
  select
    id,
    metadata,
    1 - (embedding <=> query_embedding) as similarity
  from asset_embeddings
  where 1 - (embedding <=> query_embedding) >= similarity_threshold
  order by embedding <=> query_embedding
  limit match_count;
$$;

-- RPC for cosine similarity search (RAG documents, required by LangChain)
create or replace function match_rag_documents(
  query_embedding vector(384),
  match_count int,
  filter jsonb default '{}'
)
returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
language sql stable as $$
  select
    id,
    content,
    metadata,
    1 - (embedding <=> query_embedding) as similarity
  from rag_documents
  where metadata @> filter
  order by embedding <=> query_embedding
  limit match_count;
$$;
