
FROM python:3.12
# Instalar netcat para healthcheck de broker
RUN apt-get update && apt-get install -y netcat-openbsd

EXPOSE 5000/tcp

COPY requirements.txt ./
RUN pip install --upgrade --no-cache-dir "pip<24.1" setuptools wheel
RUN pip install --no-cache-dir wheel
RUN pip install --no-cache-dir -r requirements.txt


# Copia todo el código fuente
COPY . .

# Copia el entrypoint y da permisos de ejecución
COPY entrypoint.sh /src/entrypoint.sh
RUN chmod +x /src/entrypoint.sh

# Use gunicorn so Heroku can provide the port via $PORT. Use shell form so
# the environment variable is expanded at container start time by the shell.
# Bind to 0.0.0.0 and use a reasonable number of workers (2 * CPUs + 1 is common,
# but keep it small for free dynos).
CMD exec gunicorn -b 0.0.0.0:${PORT:-5000} "alpespartners.api:create_app()" --workers 2 --threads 4
