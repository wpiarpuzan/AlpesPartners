#!/usr/bin/env python3
"""
Quick DB inspection helper for AlpesPartners.

Usage:
  python scripts/inspect_db.py --db-url $DATABASE_URL --limit 20

If --db-url is omitted the script will read DATABASE_URL or DB_URL from the environment.
"""
import argparse
import os
import json
from sqlalchemy import create_engine, select, text, Table, MetaData


def normalize_db_url(url: str) -> str:
    if url and url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql+psycopg2://', 1)
    return url


def load_table(engine, table_name: str):
    meta = MetaData()
    meta.reflect(bind=engine, only=[table_name])
    return Table(table_name, meta, autoload_with=engine)


def fetch_last(engine, table_name: str, limit: int = 20):
    try:
        table = load_table(engine, table_name)
    except Exception as e:
        return {'error': f'cannot load table {table_name}: {e}'}
    stmt = select(table).order_by(table.c.id.desc()).limit(limit)
    with engine.connect() as conn:
        res = conn.execute(stmt)
        rows = [dict(r) for r in res.mappings().all()]
    # reverse to show oldest-first
    return list(reversed(rows))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--db-url', help='Database URL (overrides env)')
    p.add_argument('--limit', type=int, default=20, help='Number of rows to fetch from each table')
    args = p.parse_args()

    db_url = args.db_url or os.getenv('DATABASE_URL') or os.getenv('DB_URL')
    if not db_url:
        print('DATABASE_URL or DB_URL must be set or passed with --db-url')
        raise SystemExit(1)
    db_url = normalize_db_url(db_url)

    engine = create_engine(db_url, future=True)

    outbox = fetch_last(engine, 'outbox', limit=args.limit)
    saga_log = fetch_last(engine, 'saga_log', limit=args.limit)

    out = {'outbox_last': outbox, 'saga_log_last': saga_log}
    print(json.dumps(out, default=str, indent=2))


if __name__ == '__main__':
    main()
