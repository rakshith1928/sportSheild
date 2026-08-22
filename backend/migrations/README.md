# Database Migrations

SQL migrations for the Supabase (Postgres + pgvector) schema. No migration
tooling is wired up — apply files in order via the Supabase SQL Editor or
`supabase db execute`:

1. `000_baseline_schema.sql` — full schema: assets, scans, violations,
   reports, the two pgvector stores, and the similarity RPCs.
2. `001_violations_severity.sql` — adds `violations.severity` (+ backfill
   and index). **Required before deploying the backend that writes it**;
   violation inserts fail against a schema without the column.
3. `002_storage_private.sql` — makes the 'assets' bucket private; clients
   get short-lived signed URLs from the backend.
4. `003_rls_policies.sql` — defense-in-depth RLS: owner-scoped SELECT for
   authed users on app tables, deny-all on vector stores and storage.
5. `004_single_source_of_truth.sql` — `assets` table becomes THE metadata
   store; `asset_embeddings` holds only (id, embedding, created_at);
   match_assets RPC now joins to assets (orphans cleaned up first).

## Conventions

- All files are idempotent (`if not exists` / `or replace`) so re-running
  is safe.
- The backend connects with the service-role key (RLS bypassed by design);
  tenancy is enforced at the API layer. See the header of 000 before
  exposing tables to client SDKs.
- When changing schema-touching code, add a new numbered migration here in
  the same commit.
