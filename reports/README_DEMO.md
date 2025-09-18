Demo run artifacts

What this folder contains:
- newman-report.txt — human-readable transcript of the successful Postman run
- newman-summary.json — small JSON summary with counts and timings

How to reproduce locally (PowerShell)

1) Start/restart the app (mounts the workspace so the running container uses your host edits):

docker rm -f alpespartner 2>$null
docker run -d --name alpespartner --network alpespartners_sidecar -p 5000:5000 `
  -v "C:\Users\juanp\Documents\MISO\Bimestre 8\No Mono\AlpesPartners:/src:ro" `
  -e PYTHONPATH=/src/src -e MESSAGE_BUS=DB_OUTBOX -e MIGRATE_ON_START=true `
  -e "DB_URL=postgresql+psycopg2://admin:admin10100101.@postgres:5432/postgres" `
  alpespartner:local /bin/bash /src/entrypoint.sh

2) Install newman (if not already):

npm install newman --no-save

3) Run the Postman collection (use a delay to avoid race with async outbox worker):

npx newman run postman/entrega5-saga.postman_collection.json `
  --env-var "BASE_URL=http://localhost:5000" --delay-request 4000

4) Optional checks in Postgres:

docker exec -i postgres psql -U admin -d postgres -c "select id, topic, event_type, status, created_at, updated_at from outbox order by id desc limit 20;"

docker exec -i postgres psql -U admin -d postgres -c "select id, saga_id, step, step_id, type, status, payload, ts from saga_log order by id desc limit 50;"

Notes and tips
- The demo runs the Flask dev server and a simple DB outbox poller; in production use a proper WSGI and robust worker.
- Tests use an explicit fixed-delay to avoid flakes; you can make them fully robust by replacing the fixed delay with a polling script that waits for the saga final state.
- If you mount the repo into the container, set PYTHONPATH=/src/src so Python can import the `alpespartners` package.

