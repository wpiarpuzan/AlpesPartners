# Lightweight Postgres image for AlpesPartners
# Builds on the official Postgres image and copies the init SQL into
# /docker-entrypoint-initdb.d so the DB is initialized on first run.

FROM postgres:15-alpine

# Set a default user/password; override at runtime with environment variables
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=admin10100101.
ENV POSTGRES_DB=postgres

# Copy initialization SQL files and helper script into the image
COPY pulsar-manager/sql/pulsar_manager_tables.sql /docker-entrypoint-initdb.d/pulsar_manager_tables.sql
COPY pulsar-manager/sql/alpespartner_tables.sql /docker-entrypoint-initdb.d/alpespartner_tables.sql
COPY docker/postgres/init-dbs.sh /docker-entrypoint-initdb.d/init-dbs.sh
RUN chmod +x /docker-entrypoint-initdb.d/init-dbs.sh

# Expose the default Postgres port
EXPOSE 5432

# Entrypoint is the same as the official image
CMD ["postgres"]
