import os
import sys
import time
from urllib.parse import urlparse
import psycopg2

MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'migrations')


def get_db_url():
    # Prefer DATABASE_URL then DB_URL
    return os.environ.get('DATABASE_URL') or os.environ.get('DB_URL')


def wait_for_db(host, port, timeout=60):
    """Wait for a TCP connection to host:port to become available.

    We avoid requiring DB authentication for the wait check because some
    Postgres images are configured with non-default users/passwords and
    psycopg2 would fail authentication even when the TCP port is open.
    """
    import socket

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, int(port)), timeout=3):
                return True
        except Exception:
            time.sleep(2)
    return False


def apply_migration(conn, sql):
    with conn.cursor() as cur:
        cur.execute(sql)


def main():
    db_url = get_db_url()
    if not db_url:
        print('No DB_URL or DATABASE_URL provided; skipping migrations')
        return 0

    parsed = urlparse(db_url)
    host = parsed.hostname or 'localhost'
    port = parsed.port or 5432
    user = parsed.username or 'postgres'
    password = parsed.password or None
    dbname = (parsed.path or '').lstrip('/') or 'postgres'

    print(f'Waiting for DB at {host}:{port}...')
    if not wait_for_db(host, port, timeout=120):
        print(f'ERROR: DB at {host}:{port} not reachable after timeout')
        return 2

    print('DB reachable, applying migrations...')
    conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname)
    try:
        # Apply SQL files in lexicographic order
        files = sorted([f for f in os.listdir(MIGRATIONS_DIR) if f.endswith('.sql')])
        for fname in files:
            path = os.path.join(MIGRATIONS_DIR, fname)
            print(f'Applying {path}')
            with open(path, 'r', encoding='utf-8') as fh:
                sql = fh.read()
            apply_migration(conn, sql)
            conn.commit()
        print('Migrations applied successfully')
    finally:
        conn.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
