# E2E demo helper

This folder contains end-to-end demo scripts for AlpesPartners. They are written to run inside the `docker-compose` environment and do not require `psql` or `pulsar-client` on the host; the scripts use `docker exec`.

Quick run (from this directory):

```bash
./demo_run.sh
```

Individual scenarios:
- `./up.sh` - start the stack
- `./happy_path.sh` - simulate a payment approved flow
- `./compensacion.sh` - simulate a payment reversal/cancel flow
- `./idempotencia.sh` - send the same PagoConfirmado twice and check idempotency (isolated per run)
- `./outbox.sh` - quick check of the outbox table
- `./summary.sh` - prints counts and recent rows from the main demo tables for quick inspection
- `./down.sh` - stop and remove volumes

Notes:
- `idempotencia.sh` generates a timestamped campaign id per run so results are isolated.
- If `outbox` appears empty, the app may be publishing events directly instead of using the outbox path for the simulated flows; run `./summary.sh` and check app logs for outbox/poller activity.
