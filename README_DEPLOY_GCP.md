# Despliegue mínimo en GKE (Autopilot) con 4 microservicios + Postgres + BFF público

> BD y Pulsar **dentro del clúster**. BFF expuesto con IP pública. Cliente/Campanias/Pagos internos.

## 0) Pre-requisitos
- gcloud SDK, kubectl, helm, Docker.
- Proyecto GCP ya seleccionado: `gcloud config set project <TU_PROYECTO>`
- Asegúrate de estar logueado en GCP.

## 1) Crear clúster

Ejecute el bash que crea el cluster en GCP

```bash
bash config_cluster.bash
```

## 2) Configurar Pulsar dentro del clúster

Ejecute el bash que crea el repositorio de imagenes las compila y las sube a GCP

```bash
bash config_pulsar.bash
```

## 3) Construir y subir imágenes

Ejecute el bash que crea el repositorio de imagenes las compila y las sube a GCP

```bash
bash config_images.bash
```

## 4) Desplegar manifests

```bash
bash config_manifests.bash
```

## 5) Obtener IP pública del BFF y probar

```bash
kubectl -n alpes get svc bff -w
# cuando aparezca EXTERNAL-IP
echo http://$(kubectl -n alpes get svc bff -o jsonpath='{.status.loadBalancer.ingress[0].ip}')/api/v1/health
```

