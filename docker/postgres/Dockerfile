# Lightweight Postgres image for AlpesPartners
# Builds on the official Postgres image and copies the init SQL into
# /docker-entrypoint-initdb.d so the DB is initialized on first run.

FROM postgres:15-alpine

# Set a default user/password; override at runtime with environment variables
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=admin10100101.
ENV POSTGRES_DB=postgres

# Copy initialization SQL (read-only in the image)
# This file exists in the repo at: ./pulsar-manager/sql/init.sql
COPY ../../pulsar-manager/sql/init.sql /docker-entrypoint-initdb.d/init.sql

# Expose the default Postgres port
EXPOSE 5432

# Entrypoint is the same as the official image
CMD ["postgres"]
