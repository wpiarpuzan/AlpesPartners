web: gunicorn -b 0.0.0.0:${PORT} "alpespartners.api:create_app()"
# Set RUN_AS_WORKER=1 so module initializers know this process is the worker
worker: RUN_AS_WORKER=1 python -m alpespartners.infra.message_bus.worker