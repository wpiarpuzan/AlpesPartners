# Postgres Image for AlpesPartners

This small helper builds a Postgres image that contains the project SQL initialization script so you can deploy the DB as a self-contained image to a cloud registry.

Files
- `docker/postgres/Dockerfile` - builds a Postgres image including `pulsar-manager/sql/init.sql`.

How to build locally
```powershell
# From project root
docker build -t alpespartners-postgres:latest -f docker/postgres/Dockerfile .
```

How to test
```powershell
# Run the image locally
docker run --rm -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin10100101. -p 5432:5432 --name alpes-db alpespartners-postgres:latest
# Wait a few seconds then test connection
psql "postgresql://admin:admin10100101.@localhost:5432/postgres" -c "SELECT 1;"
```

How to push to a registry
```powershell
# Tag and push
docker tag alpespartners-postgres:latest <your-registry>/alpespartners-postgres:latest
docker push <your-registry>/alpespartners-postgres:latest
```

Notes
- The init SQL is copied into the image so the DB will initialize when run with an empty data directory. If you're deploying to production/cloud you'll likely mount a persistent volume and/or use a managed Postgres service instead. This image is convenient for quick cloud deploys where you want control over initial schema/data.
- You can override `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB` at runtime with environment variables.
