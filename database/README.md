# Database

This directory stores reproducible SQL for the shared Supabase database.

## F-1 Apply Order

1. Run `migrations/202606160001_create_properties.sql` in Supabase SQL Editor.
2. Run `seed/transaction_history_seed.sql` in Supabase SQL Editor.
3. Run `seed/properties_seed.sql` in Supabase SQL Editor.

Seed SQL is generated from normalized transaction rows and the geocoding cache with:

```bash
python scripts/seed/generate_properties_seed.py
```

Secrets, connection strings, geocoding API keys, and service role keys must not be committed.
