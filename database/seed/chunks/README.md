# Seed SQL Chunks

Supabase SQL Editor may reject very large SQL files. Run these chunk files in order.

1. Run all `transaction_history_seed_*.sql` files in numeric order.
2. Run all `properties_seed_*.sql` files in numeric order.

- transaction chunks: 17
- property chunks: 1

## What These Files Are

These chunk files are generated bootstrap SQL for F-1 only.

- `transaction_history_seed_*.sql`: inserts normalized MOLIT real-transaction rows.
- `properties_seed_*.sql`: inserts dummy property listings generated from real transaction building anchors.

They exist because Supabase SQL Editor rejects the single large seed SQL file. Run chunks in numeric order.

## When To Delete

Delete this directory after Spring Batch can populate `transaction_history` and `properties` directly, and after BE/FE no longer need this static seed dataset for map development.
