# Running AlpesPartners locally with docker compose

This repository includes an opinionated docker-compose that starts Pulsar, Postgres instances and the microservices.

Quick start

1. Copy example environment:

   cp .env.example .env

2. Start the stack:

   docker compose up -d

   The `entrypoint.sh` script will:
   - parse `DB_URL` or `DATABASE_URL` from environment
   - wait until the DB host is resolvable and accepting connections
   - run SQL migrations from `migrations/` (files applied in lexical order)
   - wait for Pulsar broker if `START_CONSUMERS=1` and launch consumers
   - start the Flask app

3. To tail logs:

   docker compose logs -f bff

Migrations

- Place SQL migration files in `migrations/` with names like `V1__init_schema.sql`, `V2__...sql`.
- The entrypoint runs the `src/alpespartners/scripts/run_migrations.py` script which applies all `.sql` files found there.

Notes

- The compose file already sets `DB_URL` for most services; if you run the stack in another cloud, ensure the service names or hostnames match your environment or set `DB_URL` appropriately.
- For production deployments you should use a proper migration tool (Alembic) with versioned migrations and transactional upgrades.
