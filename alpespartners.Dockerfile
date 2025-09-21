
FROM python:3.12
# Instalar netcat para healthcheck de broker
RUN apt-get update && apt-get install -y netcat-openbsd

EXPOSE 5000/tcp

COPY requirements.txt ./
RUN pip install --upgrade --no-cache-dir "pip<24.1" setuptools wheel
RUN pip install --no-cache-dir wheel
RUN pip install --no-cache-dir -r requirements.txt


# Copiar migraciones explícitamente para que estén disponibles en tiempo de ejecución
# Esto evita que el entrypoint falle cuando busca /src/migrations
COPY migrations /src/migrations

# Copia todo el código fuente
COPY . .

# Copia el entrypoint y da permisos de ejecución
COPY entrypoint.sh /src/entrypoint.sh
RUN chmod +x /src/entrypoint.sh
# Ensure entrypoint has LF line endings (strip CR) to avoid /bin/sh CR issues
RUN sed -i 's/\r$//' /src/entrypoint.sh || true

CMD [ "flask", "--app", "./src/alpespartners/api", "run", "--host=0.0.0.0"]
