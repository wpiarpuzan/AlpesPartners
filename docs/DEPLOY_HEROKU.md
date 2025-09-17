Deploying AlpesPartners to Heroku (DB Outbox mode)

This guide shows a minimal path to deploy the demo to Heroku and run the Postman/Newman tests against the Heroku-deployed app.

Prerequisites
- Heroku CLI installed and you have an account
- Git configured with your Heroku app remote (or you can use `heroku container:push`)
- A Postgres add-on provisioned on Heroku (e.g., Heroku Postgres)

Overview
- We'll run the app in DB_OUTBOX mode on Heroku (no Pulsar broker). The `Procfile` is present and uses Gunicorn.
- Use the Heroku Postgres database for both app data and the outbox table.

Steps
1) Create the Heroku app (if you don't have one):

heroku create <your-app-name>

2) Provision a Postgres add-on (choose the plan you need):

heroku addons:create heroku-postgresql:hobby-basic -a <your-app-name>

3) Set required environment variables:

# Enable DB outbox mode and auto-migrations
heroku config:set MESSAGE_BUS=DB_OUTBOX MIGRATE_ON_START=true -a <your-app-name>

# (Heroku will set DATABASE_URL automatically when you provision Postgres)
# If you need other env vars, set them too (for example, TOPIC names or retry settings)

4) Option A — Deploy with Git (buildpacks / Python)

# Commit changes and push to Heroku
git add .
git commit -m "Deploy: enable DB_OUTBOX demo"
git push heroku HEAD:master

# Scale web dyno
heroku ps:scale web=1 -a <your-app-name>

4b) Option B — Deploy docker image to Heroku container registry

# Build image locally and push
heroku container:login
heroku container:push web -a <your-app-name>
heroku container:release web -a <your-app-name>

5) Run one-off migrations (if MIGRATE_ON_START is false) or verify they ran at startup.

heroku run bash -a <your-app-name>
# inside dyno
python -c "from alpespartners.config.migrations import run_startup_migrations; run_startup_migrations()"

6) Confirm the app is up:

heroku open -a <your-app-name>
# or curl
curl -sS https://<your-app-name>.herokuapp.com/saga/health | jq .

7) Run Postman/Newman against Heroku

# Locally, install newman if not present
npm install newman --no-save

# Run the collection pointing at the Heroku base URL
npx newman run postman/entrega5-saga.postman_collection.json --env-var "BASE_URL=https://<your-app-name>.herokuapp.com" --delay-request 4000

Notes and caveats
- On Heroku the DATABASE_URL env var is automatically provided by the Postgres add-on. The demo's migrations will create the `outbox` and `saga_log` tables.
- The demo uses the Flask development server inside the container in local runs. Heroku will use the `Procfile` with Gunicorn which is more production-like.
- If you choose container deployment, ensure the image sets the correct `PYTHONPATH` (the Dockerfile in this project copies into /src). The `Procfile` provided is: web: gunicorn -b 0.0.0.0:${PORT} "alpespartners.api:create_app()"
- For reliable automated testing, prefer polling for saga final state rather than fixed delays.

Troubleshooting
- If you see missing columns errors, run the migration command manually via `heroku run`.
- If your Heroku dyno cannot reach external services, confirm no listeners to Pulsar are required in DB_OUTBOX mode.

