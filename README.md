## 🗄️ Estrategia de Persistencia y CRUD

### Base de Datos Centralizada
En este proyecto se utiliza un **estilo centralizado de base de datos** (PostgreSQL) para todos los módulos. Esta decisión facilita la prueba y evaluación de los escenarios escogidos, ya que permite una gestión y monitoreo más simple de los datos, así como una depuración más directa durante el desarrollo y las pruebas.

### Enfoque CRUD
Actualmente, el sistema implementa operaciones **CRUD** (Create, Read, Update, Delete) tradicionales sobre las entidades principales. Aunque la arquitectura soporta Event Sourcing, para este contexto de pruebas se opta por CRUD por las siguientes razones:
- **Simplicidad**: CRUD es más fácil de implementar y entender para pruebas rápidas.
- **Facilidad de validación**: Permite verificar el estado actual de los datos sin reconstrucción desde eventos.
- **Menor complejidad**: Reduce la curva de aprendizaje y el tiempo de setup para el equipo y los evaluadores.
- **Compatibilidad**: Facilita la integración con herramientas de testing y reporting convencionales.

> **Nota:** Event Sourcing es ideal para escenarios de auditabilidad y reconstrucción histórica, pero en pruebas y validaciones funcionales CRUD permite iterar y validar más rápido.

### Escalabilidad: Escenario Probado
Para pruebas de escalabilidad, se está evaluando el **escenario número 2**, que implica la centralización de la base de datos y la optimización de los accesos concurrentes. Este enfoque permite observar el comportamiento del sistema bajo carga y validar la robustez de la arquitectura centralizada antes de considerar una migración a event sourcing distribuido.

## 👥 Equipo
- Willian Andres Piarpuzan
- Karen Fernanda Tarazona
- Juan Pablo Camacho
- Yelsit Felipe Rivera


## Descripción General

**Alpes Partners** es una plataforma empresarial basada en microservicios, diseñada con Domain-Driven Design (DDD), CQRS. El sistema gestiona operaciones de socios, clientes y pagos de forma escalable y robusta, integrando Apache Pulsar como broker de eventos y PostgreSQL como base de datos principal.

### Arquitectura
- **DDD**: Separación clara de dominios y lógica de negocio.
- **CQRS**: Comandos y queries desacoplados para optimizar lecturas y escrituras.
- **Unit of Work**: Consistencia transaccional y disparo automático de eventos.
- **Pulsar**: Comunicación asíncrona entre módulos mediante tópicos de comandos y eventos.
- **Flask**: API REST y Backend For Frontend (BFF).

### Estructura del Proyecto

```
src/
├── alpespartners/
│   ├── seedwork/         # Kernel compartido: entidades base, eventos, UoW
│   ├── modulos/         # Bounded Contexts: campanias, cliente, pagos
│   ├── api/             # Endpoints REST (Flask blueprints)
│   ├── config/          # Configuración DB y UoW
```

Cada módulo sigue la estructura DDD estándar:
```
modulos/{nombre}/
├── aplicacion/
│   ├── comandos/     # Command handlers (@singledispatch)
│   ├── queries/      # Query handlers (@singledispatch)
│   ├── dto.py        # Data Transfer Objects
│   └── mapeadores.py # Mappers (Domain ↔ DTO)
├── dominio/
│   ├── entidades.py  # Aggregate roots, entities
│   ├── eventos.py    # Domain events
│   ├── objetos_valor.py  # Value objects
│   └── repositorios.py   # Repository interfaces
├── infraestructura/
│   ├── consumidores.py   # Pulsar event consumers
│   ├── publisher.py      # Event publishers
│   └── event_store.py    # Event sourcing store
```

### Stack Tecnológico

| Componente         | Tecnología         | Propósito                  |
|--------------------|-------------------|----------------------------|
| Backend            | Python 3.12+      | Lógica principal           |
| Framework Web      | Flask             | API REST + BFF             |
| Base de Datos      | PostgreSQL        | Persistencia principal     |
| Event Broker       | Apache Pulsar     | Mensajería asíncrona       |
| ORM                | SQLAlchemy        | Mapeo objeto-relacional    |
| Testing            | pytest + coverage | Pruebas y cobertura        |
| Contenedores       | Docker Compose    | Orquestación               |

### Patrones Clave
- **CQRS**: Separación de comandos y queries con handlers y decoradores.
- **Unit of Work**: Transacciones y disparo de eventos.
- **Eventos de Dominio e Integración**: Comunicación entre módulos vía Pulsar.

### Comunicación Entre Módulos
- **Comandos**: `comandos.{modulo}` (ej: `comandos.campanias`)
- **Eventos**: `eventos.{modulo}` (ej: `eventos.pagos`)

### Modelo de Datos
- **Cliente**: `ClienteNatural` (clientes)
- **Pagos**: `Payout`, `Transaction` (payouts, transactions)
- **Campanias**: `Campania` (event store)

### Testing
- Mock de servicios externos
- Reporte de cobertura con `coverage`

### Observabilidad
- Logs detallados
- Métricas básicas

## Cómo ejecutar el proyecto

### Configuración rápida

Ejecuta el siguiente comando para preparar el entorno:

```bash
bash .devcontainer/setup.sh
```

### Levantar el stack completo (incluye Pulsar y BD)

```bash
docker compose --profile pulsar --profile bd --profile alpespartner up -d
```

### Ejecución local (solo API)

```bash
flask --app src/alpespartners/api --debug run
```

### Ejecutar pruebas

```bash
coverage run -m pytest && coverage report
```

### Crear imagen Docker

```bash
docker build . -f alpespartners.Dockerfile -t alpespartners/flask
```

### Ejecutar contenedor (sin compose)

```bash
docker run -p 5000:5000 alpespartners/flask
```

## AlpesPartner
### Ejecutar Aplicación

Desde el directorio principal ejecute el siguiente comando.

```bash
flask --app src/alpespartners/api run
```

Siempre puede ejecutarlo en modo DEBUG:

```bash
flask --app src/alpespartners/api --debug run
```

### Ejecutar pruebas

```bash
coverage run -m pytest
```

### Ver reporte de covertura
```bash
coverage report
```

### Crear imagen Docker

Desde el directorio principal ejecute el siguiente comando.

```bash
docker build . -f alpespartners.Dockerfile -t alpespartners/flask
```

### Ejecutar contenedora (sin compose)

Desde el directorio principal ejecute el siguiente comando.

```bash
docker run -p 5000:5000 alpespartners/flask

```

# BFF Web UI - Backend For Frontend

## Descripción
Backend For Frontend optimizado para interfaces web del sistema Alpes Partners. Implementa **arquitectura hexagonal** con comunicación HTTP a microservicios, siguiendo principios de **autonomía y desacoplamiento**.

### Hexagonal Architecture
```
📁 bff/
├── 🏛️ domain/           # Dominio del BFF
│   ├── models/          # Modelos específicos para UI web
│   └── exceptions/      # Excepciones del dominio BFF
├── 🎯 application/      # Casos de uso y puertos
│   ├── use_cases/       # Casos de uso web-optimizados
│   └── ports/           # Interfaces (puertos de entrada/salida)
└── 🔧 infrastructure/   # Adaptadores e infraestructura
    ├── http_client.py   # 🆕 Cliente HTTP para microservicios
    ├── adapters/        # Adaptadores HTTP (no imports directos)
    ├── web/            # Framework web (Flask)
    └── config.py       # Inyección de dependencias
```

### Comunicación HTTP
```
┌─────────────────┐    HTTP REST    ┌─────────────────────────┐
│   Frontend      │ ──────────────► │      BFF (5001)         │
│   (React/Vue)   │ ◄────────────── │   • Dashboard           │
└─────────────────┘                 │   • Agregación          │
                                    │   • Cache               │
                                    │   • Validación          │
                                    └─────────────────────────┘
                                               │ HTTP REST
                                               ▼
                                    ┌─────────────────────────┐
                                    │  AlpesPartners (5000)   │
                                    │   • /cliente/registrar  │
                                    │   • /pagos/pagar        │ 
                                    │   • /campanias/crear    │
                                    └─────────────────────────┘
```

## 🔧 Configuración y Ejecución

### Variables de Entorno Críticas
```bash
# URLs de servicios backend
ALPESPARTNERS_SERVICE_URL=http://localhost:5000  # 🎯 URL base microservicios

# Configuración BFF
BFF_HOST=0.0.0.0
BFF_PORT=5001
BFF_DEBUG=true
BFF_HTTP_TIMEOUT=30

# Ver .env.bff.example para configuración completa
```

### Ejecución Local
```bash
# 1. Iniciar servicios backend (AlpesPartners)
cd src
flask --app alpespartners/api --debug run --port 5000

# 2. En otro terminal, iniciar BFF
cd src
export ALPESPARTNERS_SERVICE_URL=http://localhost:5000
python -m bff.main
```

### Con Flask directamente
```bash
export FLASK_APP=bff.infrastructure.web.app:create_bff_app
export ALPESPARTNERS_SERVICE_URL=http://localhost:5000
flask run --port 5001 --debug
```

## 🌐 APIs del BFF

### Endpoints Principales
| Endpoint | Método | Descripción | Backend |
|----------|---------|-------------|---------|
| `/api/v1/health` | GET | Health check + estado servicios | - |
| `/api/v1/dashboard` | GET | Datos agregados dashboard | Múltiples |
| `/api/v1/clientes` | GET | Lista paginada clientes | HTTP → `/cliente/{id}` |
| `/api/v1/clientes/{id}` | GET | Detalle cliente + datos relacionados | HTTP → múltiples endpoints |
| `/api/v1/clientes` | POST | Crear cliente | HTTP → `/cliente/registrar` |
| `/api/v1/pagos` | GET | Lista paginada pagos | HTTP → `/pagos/{id}` |
| `/api/v1/pagos/{id}` | GET | Detalle pago | HTTP → `/pagos/{id}` |
| `/api/v1/campanias` | GET | Lista campañas | HTTP → `/campanias/{id}` |
| `/api/v1/search` | GET | Búsqueda integrada multi-servicio | HTTP → múltiples |

## 📦 Deployment

### Docker Compose (Ejemplo)
```yaml
version: '3.8'
services:
  alpespartners-core:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_APP=alpespartners/api
    
  bff-web:
    build: 
      context: .
      dockerfile: bff.Dockerfile
    ports:
      - "5001:5001"
    environment:
      - ALPESPARTNERS_SERVICE_URL=http://alpespartners-core:5000
    depends_on:
      - alpespartners-core
```
