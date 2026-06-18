# Database

This directory stores reproducible SQL for the shared Supabase database.

## F-1 Apply Order

1. Run `migrations/202606160001_create_properties.sql` in Supabase SQL Editor.
2. Run all `seed/chunks/transaction_history_seed_*.sql` files in numeric order.
3. Run all `seed/chunks/properties_seed_*.sql` files in numeric order.

The single SQL files in `seed/transaction_history_seed.sql` and `seed/properties_seed.sql` are useful for local database clients, but they may be too large for Supabase SQL Editor.

Seed SQL is generated from normalized transaction rows and the geocoding cache with:

```bash
python scripts/seed/generate_properties_seed.py
```

Secrets, connection strings, geocoding API keys, and service role keys must not be committed.

## Local Environment

For local seed generation and future direct DB apply scripts, keep secrets in `.env.local`:

```env
NAVER_MAPS_CLIENT_ID=
NAVER_MAPS_CLIENT_SECRET=
SUPABASE_DB_URL=
SUPABASE_SERVICE_ROLE_KEY=
```

Current F-1 database application is manual: copy the SQL files into Supabase SQL Editor and run them in the order above.

Do not use `SUPABASE_SERVICE_ROLE_KEY` in the frontend. It is only for backend, batch, seed, or admin scripts.

Direct SQL execution from local scripts requires a PostgreSQL client such as `psql` or a Python driver such as `psycopg`. If those tools are not installed, use Supabase SQL Editor.
