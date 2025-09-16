# 📊 Alpes Partners - Documentación Completa de APIs y Análisis Técnico

## 🌐 APIs Expuestas

### 🔧 APIs de Sistema

#### `/health`
- **Método:** `GET`
- **Descripción:** Health check del servicio
- **Response:**
```json
{
  "status": "up"
}
```

#### `/spec`
- **Método:** `GET`
- **Descripción:** Especificación Swagger del API
- **Response:** Documento Swagger JSON completo

#### `/metrics`
- **Método:** `GET`
- **Descripción:** Métricas de observabilidad del sistema
- **Response:**
```json
{
  "count": 150,
  "errors": 2,
  "p50": 45.2,
  "p95": 120.8,
  "p99": 250.3
}
```

### 👥 Módulo Cliente

#### `POST /cliente/registrar`
- **Descripción:** Registra un nuevo cliente en el sistema
- **Content-Type:** `application/json`
- **Request Body:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nombre": "Juan Pérez",
  "email": "juan.perez@example.com",
  "cedula": "12345678",
  "fecha_nacimiento": "1985-03-15T00:00:00"
}
```
- **Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nombre": "Juan Pérez",
  "email": "juan.perez@example.com",
  "cedula": "12345678",
  "fecha_nacimiento": "1985-03-15T00:00:00"
}
```
- **Response (400):** Error de dominio
```json
{
  "error": "Email ya existe en el sistema"
}
```

#### `GET /cliente/{cliente_id}`
- **Descripción:** Obtiene información detallada de un cliente por ID
- **Path Parameters:**
  - `cliente_id` (string): UUID del cliente
- **Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nombre": "Juan Pérez",
  "email": "juan.perez@example.com",
  "fecha_registro": "2024-01-15T10:30:00",
  "total_pagos": 5,
  "ultimo_pago": "2024-09-10T14:25:00"
}
```
- **Response (404):**
```json
{
  "message": "No encontrado"
}
```

### 💳 Módulo Pagos

#### `POST /pagos/pagar`
- **Descripción:** Procesa un pago de forma asíncrona (CQRS)
- **Content-Type:** `application/json`
- **Request Body:**
```json
{
  "partner_id": "PARTNER001",
  "cycle_id": "CYCLE-2024-09",
  "total_amount": 1250.50,
  "currency": "USD",
  "payment_method_type": "CREDIT_CARD",
  "payment_method_mask": "****1234",
  "confirmation_id": "CONF-789456123",
  "processed_at": "2024-09-13T10:30:00",
  "completed_at": "2024-09-13T10:32:15"
}
```
- **Response (202):** Procesamiento aceptado
```json
{
  "id": "payout-550e8400-e29b-41d4"
}
```
- **Response (400):** Error de dominio
```json
{
  "error": "Partner no encontrado"
}
```
- **Response (500):** Error interno
```json
{
  "error": "Database connection failed",
  "trace": "Traceback (most recent call last)..."
}
```

#### `GET /pagos/{id}`
- **Descripción:** Obtiene información de un pago específico
- **Path Parameters:**
  - `id` (string): ID del payout
- **Response (200):**
```json
{
  "id": "payout-550e8400-e29b-41d4",
  "partner_id": "PARTNER001",
  "cycle_id": "CYCLE-2024-09",
  "estado": "COMPLETADO",
  "monto_total": {
    "valor": 1250.50,
    "moneda": "USD"
  },
  "fecha_creacion": "2024-09-13T10:30:00",
  "fecha_actualizacion": "2024-09-13T10:32:15"
}
```
- **Response (404):**
```json
{
  "error": "Payout no encontrado"
}
```

### 🎯 Módulo Campanias

#### `POST /campanias/comandos/crear`
- **Descripción:** Crea una nueva campaña (actualmente mock)
- **Content-Type:** `application/json`
- **Request Body:**
```json
{
  "idCampania": "CAMP001",
  "idCliente": "550e8400-e29b-41d4-a716-446655440000",
  "itinerario": ["Madrid", "Barcelona", "Valencia"]
}
```
- **Response (202):**
```json
{
  "message": "Campania creada (mock)",
  "data": {
    "idCampania": "CAMP001",
    "idCliente": "550e8400-e29b-41d4-a716-446655440000",
    "itinerario": ["Madrid", "Barcelona", "Valencia"]
  }
}
```

#### `GET /campanias/{id_campania}`
- **Descripción:** Obtiene información de una campaña (actualmente mock)
- **Path Parameters:**
  - `id_campania` (string): ID de la campaña
- **Response (200):**
```json
{
  "message": "Campania CAMP001 (mock)"
}
```

---

## 🌐 Backend For Frontend (BFF) Web UI

### 📋 Descripción del BFF

El **Backend For Frontend (BFF)** es una capa de agregación especializada que optimiza las APIs para interfaces web. Implementa **Arquitectura Hexagonal** con las mejores prácticas de desarrollo empresarial.

**Puerto por defecto:** `5001`  
**Base URL:** `http://localhost:5001/api/v1`

### 🏗️ Arquitectura Hexagonal del BFF

```
📁 bff/
├── 🏛️ domain/              # Dominio del BFF
│   ├── models/             # Modelos específicos para UI web
│   │   ├── dashboard.py    # Agregaciones de datos
│   │   ├── cliente_view.py # Vista compuesta de cliente
│   │   └── search_result.py # Resultados de búsqueda
│   └── exceptions/         # Excepciones del dominio BFF
├── 🎯 application/         # Casos de uso y puertos
│   ├── use_cases/          # Casos de uso específicos para web
│   │   ├── dashboard.py    # Generar dashboard aggregado
│   │   ├── cliente.py      # Gestión de clientes optimizada
│   │   ├── pagos.py        # Consultas de pagos paginadas
│   │   └── search.py       # Búsqueda integrada multi-servicio
│   └── ports/              # Interfaces (puertos de entrada/salida)
└── 🔧 infrastructure/      # Adaptadores e infraestructura
    ├── adapters/           # Adaptadores para servicios backend
    │   ├── cliente.py      # Adaptador servicio Cliente
    │   ├── pagos.py        # Adaptador servicio Pagos
    │   └── campanias.py    # Adaptador servicio Campañas
    ├── web/               # Framework web (Flask)
    │   ├── controllers/    # Controladores REST
    │   ├── schemas/       # Schemas de validación
    │   └── app.py         # Factory de aplicación Flask
    └── config.py          # Configuración e inyección de dependencias
```

### 🚀 APIs del BFF

#### 📊 Dashboard Agregado

##### `GET /api/v1/dashboard`
- **Descripción:** Datos agregados para dashboard principal
- **Response (200):**
```json
{
  "total_clientes": 1250,
  "total_pagos": 8500,
  "total_campanias": 45,
  "pagos_recientes": [
    {
      "id": "payout-123",
      "partner_id": "PARTNER001",
      "monto": 1500.00,
      "fecha": "2024-01-15T10:30:00Z"
    }
  ],
  "clientes_recientes": [
    {
      "id": "cliente-456",
      "nombre": "Juan Pérez",
      "email": "juan@example.com"
    }
  ]
}
```

#### 👥 Clientes Optimizado para Web

##### `GET /api/v1/clientes`
- **Descripción:** Lista paginada de clientes con filtros
- **Query Parameters:**
  - `page` (int): Número de página (default: 1)
  - `per_page` (int): Elementos por página (default: 20, max: 100)
  - `search` (string): Término de búsqueda (nombre/email)
  - `sort_by` (string): Campo de ordenamiento (nombre|fecha_registro)
  - `sort_order` (string): Orden (asc|desc)
- **Response (200):**
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nombre": "Juan Pérez",
      "email": "juan.perez@example.com",
      "fecha_registro": "2024-01-15T10:30:00Z",
      "total_pagos": 5,
      "ultimo_pago": "2024-09-10T14:25:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

##### `GET /api/v1/clientes/{id}`
- **Descripción:** Vista detallada de cliente con datos relacionados
- **Path Parameters:**
  - `id` (string): UUID del cliente
- **Response (200):**
```json
{
  "cliente": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nombre": "Juan Pérez",
    "email": "juan.perez@example.com",
    "cedula": "12345678",
    "fecha_registro": "2024-01-15T10:30:00Z"
  },
  "estadisticas": {
    "total_pagos": 5,
    "monto_total": 7500.00,
    "primer_pago": "2024-02-01T09:15:00Z",
    "ultimo_pago": "2024-09-10T14:25:00Z"
  },
  "pagos_recientes": [
    {
      "id": "payout-789",
      "monto": 1500.00,
      "fecha": "2024-09-10T14:25:00Z",
      "estado": "COMPLETADO"
    }
  ],
  "campanias_activas": [
    {
      "id": "camp-001",
      "nombre": "Campaña Verano 2024",
      "estado": "ACTIVA"
    }
  ]
}
```

##### `POST /api/v1/clientes`
- **Descripción:** Crear nuevo cliente (proxy optimizado)
- **Content-Type:** `application/json`
- **Request Body:**
```json
{
  "nombre": "María González",
  "email": "maria@example.com",
  "cedula": "87654321",
  "fecha_nacimiento": "1990-05-20"
}
```
- **Response (201):**
```json
{
  "id": "nueva-uuid-generada",
  "nombre": "María González",
  "email": "maria@example.com",
  "cedula": "87654321",
  "fecha_nacimiento": "1990-05-20T00:00:00Z",
  "fecha_registro": "2024-01-15T15:45:00Z"
}
```

#### 💳 Pagos Optimizado para Web

##### `GET /api/v1/pagos`
- **Descripción:** Lista paginada de pagos con filtros avanzados
- **Query Parameters:**
  - `page` (int): Número de página
  - `per_page` (int): Elementos por página
  - `partner_id` (string): Filtrar por partner
  - `estado` (string): Filtrar por estado (PENDING|COMPLETED|FAILED)
  - `fecha_desde` (string): Fecha inicio (ISO 8601)
  - `fecha_hasta` (string): Fecha fin (ISO 8601)
  - `monto_min` (float): Monto mínimo
  - `monto_max` (float): Monto máximo
- **Response (200):**
```json
{
  "data": [
    {
      "id": "payout-550e8400",
      "partner_id": "PARTNER001",
      "cycle_id": "CYCLE-2024-09",
      "monto": 1250.50,
      "moneda": "USD",
      "estado": "COMPLETADO",
      "fecha_creacion": "2024-09-13T10:30:00Z",
      "fecha_completado": "2024-09-13T10:32:15Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 450,
    "pages": 23
  },
  "agregaciones": {
    "total_monto": 125000.50,
    "pagos_completados": 420,
    "pagos_pendientes": 25,
    "pagos_fallidos": 5
  }
}
```

##### `GET /api/v1/pagos/{id}`
- **Descripción:** Detalle completo de pago con información enriquecida
- **Path Parameters:**
  - `id` (string): ID del pago
- **Response (200):**
```json
{
  "pago": {
    "id": "payout-550e8400",
    "partner_id": "PARTNER001",
    "cycle_id": "CYCLE-2024-09",
    "monto": 1250.50,
    "moneda": "USD",
    "estado": "COMPLETADO",
    "metodo_pago": {
      "tipo": "CREDIT_CARD",
      "mascara": "****1234"
    },
    "fecha_creacion": "2024-09-13T10:30:00Z",
    "fecha_procesamiento": "2024-09-13T10:30:15Z",
    "fecha_completado": "2024-09-13T10:32:15Z"
  },
  "transacciones": [
    {
      "id": "tx-001",
      "tipo": "COMISION",
      "monto": 125.05,
      "descripcion": "Comisión 10%"
    }
  ],
  "auditoria": {
    "eventos": [
      {
        "timestamp": "2024-09-13T10:30:00Z",
        "evento": "PagoCreado",
        "usuario": "system"
      },
      {
        "timestamp": "2024-09-13T10:32:15Z", 
        "evento": "PagoCompletado",
        "usuario": "payment-processor"
      }
    ]
  }
}
```

#### 🎯 Campañas Web-Optimizada

##### `GET /api/v1/campanias`
- **Descripción:** Lista paginada de campañas (actualmente mock)
- **Query Parameters:**
  - `page` (int): Número de página
  - `per_page` (int): Elementos por página
  - `estado` (string): Filtrar por estado
- **Response (200):**
```json
{
  "data": [
    {
      "id": "camp-001",
      "nombre": "Campaña Verano 2024",
      "cliente_id": "cliente-123",
      "cliente_nombre": "Juan Pérez",
      "estado": "ACTIVA",
      "fecha_inicio": "2024-06-01T00:00:00Z",
      "fecha_fin": "2024-08-31T23:59:59Z",
      "presupuesto": 15000.00,
      "gasto_actual": 8500.00
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "pages": 3
  }
}
```

#### 🔍 Búsqueda Integrada Multi-Servicio

##### `GET /api/v1/search`
- **Descripción:** Búsqueda unificada en clientes, pagos y campañas
- **Query Parameters:**
  - `q` (string, required): Término de búsqueda
  - `type` (string): Tipo específico (cliente|pago|campania|all)
  - `limit` (int): Límite de resultados por tipo (default: 5)
- **Response (200):**
```json
{
  "query": "Juan",
  "total_results": 12,
  "results": {
    "clientes": [
      {
        "id": "cliente-123",
        "tipo": "cliente",
        "nombre": "Juan Pérez",
        "email": "juan@example.com",
        "relevancia": 0.95
      }
    ],
    "pagos": [
      {
        "id": "payout-456", 
        "tipo": "pago",
        "partner_id": "JUAN-CORP",
        "monto": 2500.00,
        "fecha": "2024-09-01T10:00:00Z",
        "relevancia": 0.80
      }
    ],
    "campanias": [
      {
        "id": "camp-789",
        "tipo": "campania", 
        "nombre": "Campaña Juan Especial",
        "cliente": "Juan Pérez",
        "relevancia": 0.85
      }
    ]
  }
}
```

#### 🏥 Health Check y Monitoreo

##### `GET /api/v1/health`
- **Descripción:** Estado de salud del BFF y servicios dependientes
- **Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "cliente_service": {
      "status": "up",
      "response_time_ms": 45
    },
    "pagos_service": {
      "status": "up", 
      "response_time_ms": 32
    },
    "campanias_service": {
      "status": "degraded",
      "response_time_ms": 1200,
      "note": "High latency detected"
    }
  },
  "cache": {
    "hits": 1250,
    "misses": 85,
    "hit_rate": 0.936
  }
}
```

### 🔧 Configuración del BFF

#### Variables de Entorno
```bash
# Servidor BFF
BFF_HOST=0.0.0.0
BFF_PORT=5001
BFF_DEBUG=false
BFF_SECRET_KEY=your-secret-key-here

# Servicios Backend (URLs de los microservicios)
CLIENTE_SERVICE_URL=http://localhost:5000
PAGOS_SERVICE_URL=http://localhost:5000  
CAMPANIAS_SERVICE_URL=http://localhost:5000

# Cache y Performance
BFF_CACHE_TIMEOUT=300
BFF_REQUEST_TIMEOUT=10
BFF_MAX_PAGE_SIZE=100
```

#### Ejecución Local
```bash
# Desde la raíz del proyecto
cd src
python -m bff.main

# Con Flask directamente
export FLASK_APP=bff.infrastructure.web.app:create_bff_app
flask run --port 5001 --debug

# Con Docker (agregar al docker-compose.yml)
docker-compose up bff-service
```

### ⚡ Características Avanzadas del BFF

#### Optimizaciones para UI Web
- ✅ **Paginación inteligente** con metadata completa
- ✅ **Búsqueda integrada** multi-servicio en una sola request
- ✅ **Vistas compuestas** (cliente + pagos + campañas)
- ✅ **Agregaciones de datos** pre-calculadas (dashboard)
- ✅ **Cache en memoria** para datos frecuentes
- ✅ **Request timeout** configurable
- ✅ **Error handling** unificado
- ✅ **Logging estructurado**

#### Patrones Implementados
- ✅ **Hexagonal Architecture** (Ports & Adapters)
- ✅ **Dependency Injection** con contenedor DI
- ✅ **Repository Pattern** via adaptadores
- ✅ **Use Case Pattern** para lógica de negocio
- ✅ **DTO Pattern** para transferencia de datos
- ✅ **Async/Await** support en Flask
- ✅ **CORS** configurado para desarrollo web
- ✅ **Schema Validation** con Marshmallow

#### Integraciones Backend
```python
# Adaptadores para cada servicio
class ClienteServiceAdapter(ClienteServicePort):
    async def get_cliente(self, id: str) -> ClienteView:
        # Integración con servicio Cliente original
        
class PagosServiceAdapter(PagosServicePort):
    async def get_pagos_paginados(self, filtros: PagosFilter) -> PaginatedPayouts:
        # Integración con servicio Pagos original
```

---

---

## 🏗️ Análisis Técnico Completo del Proyecto

### 📋 Resumen Ejecutivo

**Alpes Partners** es un sistema de microservicios desarrollado con **Domain-Driven Design (DDD)**, implementando patrones avanzados como **CQRS** (Command Query Responsibility Segregation) y **Event Sourcing**. El proyecto está diseñado para manejar operaciones de socios, clientes y pagos de forma escalable y mantenible.

### 🔧 Stack Tecnológico

| Componente | Tecnología | Versión | Propósito |
|------------|------------|---------|-----------|
| **Backend** | Python | 3.12+ | Lenguaje principal |
| **Framework Web** | Flask | 3.1.1 | API REST + BFF |
| **BFF Layer** | Flask + Hexagonal | 3.1.1 | Backend For Frontend web UI |
| **Base de Datos** | PostgreSQL | 15 | Persistencia principal |
| **ORM** | SQLAlchemy | 2.0.41 | Mapeo objeto-relacional |
| **Event Broker** | Apache Pulsar | 3.7.0 | Mensajería asíncrona |
| **Validation** | Marshmallow | 3.20.1 | Schema validation (BFF) |
| **Contenedores** | Docker + Docker Compose | - | Orquestación |
| **Testing** | pytest + coverage | 8.4.0 / 6.5.0 | Pruebas y cobertura |
| **Serialización** | Apache Avro | 3.7.0 | Esquemas de eventos |

### 🏛️ Arquitectura del Sistema

#### Estructura de Capas DDD

```
📁 src/
├── 🌐 bff/                # Backend For Frontend (Nuevo)
│   ├── domain/            # Modelos específicos UI web
│   ├── application/       # Casos de uso web-optimizados
│   └── infrastructure/    # Adaptadores y web framework
└── alpespartners/         # Core Microservicios
    ├── 🧱 seedwork/       # Shared Kernel
    │   ├── dominio/       # Entidades base, eventos, excepciones
    │   ├── aplicacion/    # Comandos, queries, handlers base
    │   ├── infraestructura/ # UoW, utilidades, esquemas
    │   └── observabilidad/ # Métricas y monitoreo
    ├── 🏢 modulos/        # Bounded Contexts
    │   ├── cliente/       # Gestión de clientes
    │   ├── pagos/         # Procesamiento de pagos
    │   └── campanias/     # Gestión de campañas
    ├── 🌐 api/            # Capa de presentación (Flask)
    └── ⚙️ config/         # Configuración (DB, UoW)
```

#### Módulos por Bounded Context

Cada módulo sigue la estructura DDD estándar:

```
📁 {modulo}/
├── 📝 aplicacion/
│   ├── comandos/          # Command handlers (@singledispatch)
│   ├── queries/           # Query handlers (@singledispatch)
│   ├── dto.py            # Data Transfer Objects
│   └── mapeadores.py     # Mappers (Domain ↔ DTO)
├── 🏛️ dominio/
│   ├── entidades.py      # Aggregate roots, entities
│   ├── eventos.py        # Domain events
│   ├── objetos_valor.py  # Value objects
│   └── repositorios.py   # Repository interfaces
└── 🔧 infraestructura/
    ├── dto.py            # SQLAlchemy models
    ├── repositorios.py   # Repository implementations
    ├── consumidores.py   # Pulsar event consumers
    ├── publisher.py      # Event publishers
    └── event_store.py    # Event sourcing store
```

### 🎯 Patrones Arquitectónicos Implementados

#### 1. CQRS (Command Query Responsibility Segregation)

**Implementación con `@singledispatch`:**

```python
# Comandos (Escritura)
@ejecutar_commando.register
def comando_registrar_cliente(comando: RegistrarCliente):
    handler = RegistrarClienteHandler()
    return handler.handle(comando)

# Queries (Lectura)
@ejecutar_query.register
def query_obtener_cliente(query: ObtenerClientePorId):
    handler = ObtenerClientePorIdHandler()
    return handler.handle(query)
```

**Características:**
- Separación clara entre operaciones de lectura y escritura
- Handlers especializados para cada comando/query
- Registro automático mediante decoradores
- Optimización independiente de lecturas y escrituras

#### 2. Unit of Work (UoW)

**Gestión transaccional con eventos:**

```python
# Registro de operaciones (no ejecución inmediata)
UnidadTrabajoPuerto.registrar_batch(repo.agregar, entidad)
UnidadTrabajoPuerto.savepoint()
UnidadTrabajoPuerto.commit()  # ← Dispara eventos de dominio e integración
```

**Beneficios:**
- Consistencia transaccional garantizada
- Eventos de dominio disparados automáticamente
- Rollback coordinado entre múltiples operaciones
- Integración con Flask a través de `g` context

#### 3. Event Sourcing

**Almacenamiento de eventos:**

```python
def append_event(aggregate_id: str, type_: str, data: Dict[str, Any]):
    record = EventStoreModel(
        aggregate_id=aggregate_id,
        aggregate_type='Campania',
        type=type_,  # ej: "CampaniaCreada.v1"
        payload=json.dumps(data),
        occurred_on=datetime.utcnow()
    )
    db.session.add(record)
    db.session.commit()
```

**Convenciones:**
- Naming: `{Entity}{Action}.v{Version}` (ej: `PagoConfirmado.v1`)
- Versionado obligatorio con `schemaVersion`
- Método `to_dict()` en todos los eventos
- Reconstrucción de estado desde eventos

#### 4. Domain Events + Integration Events

**Flujo de eventos:**

```python
# 1. Evento de Dominio (mismo proceso)
dispatcher.send(signal=f'{type(evento).__name__}Dominio', evento=evento)

# 2. Evento de Integración (Pulsar, cross-module)
dispatcher.send(signal=f'{type(evento).__name__}Integracion', evento=evento)
```

### 🔄 Comunicación Entre Módulos

#### Apache Pulsar Topics

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| **Comandos** | `comandos.{modulo}` | `comandos.campanias` |
| **Eventos** | `eventos.{modulo}` | `eventos.pagos` |

#### Patrones de Consumo

**Consumidores (Estilo Funcional):**
```python
def suscribirse_a_eventos_pagos():
    consumer = client.subscribe(TOPIC_EVENTOS_PAGOS, "campanias-sub")
    while True:
        msg = consumer.receive()
        payload = json.loads(msg.data())
        if payload["type"] == "PagoConfirmado":
            append_event(id_campania, "CampaniaAprobada.v1", data)
        consumer.acknowledge(msg)
```

**Publishers (Estilo OOP):**
```python
class EventPublisher:
    def publish_event(self, event_type: str, data: dict):
        message = {"type": event_type, "data": data}
        self.producer.send(json.dumps(message))
```

### 🗄️ Modelo de Datos

#### Entidades Principales

| Módulo | Entidad | Tabla | Campos Clave |
|--------|---------|-------|--------------|
| **Cliente** | `ClienteNatural` | `clientes` | `id`, `nombre`, `email`, `cedula`, `total_pagos` |
| **Pagos** | `Payout` | `payouts` | `id`, `partner_id`, `cycle_id`, `monto`, `estado` |
| **Pagos** | `Transaction` | `transactions` | `id`, `partner_id`, `comision`, `event_type` |
| **Campanias** | `Campania` | `event_store` | Event sourcing (sin tabla entidad) |

#### Event Store Schema

```sql
CREATE TABLE event_store (
    id SERIAL PRIMARY KEY,
    aggregate_id VARCHAR NOT NULL,
    aggregate_type VARCHAR NOT NULL,
    type VARCHAR NOT NULL,           -- ej: "CampaniaCreada.v1"
    payload JSONB NOT NULL,
    occurred_on TIMESTAMP NOT NULL,
    INDEX(aggregate_id, aggregate_type)
);
```

### 🔒 Patrones de Seguridad y Validación

#### Value Objects
```python
@dataclass
class Email:
    valor: str
    dominio: str
    es_empresarial: bool

@dataclass  
class Cedula:
    numero: str
    
    def __post_init__(self):
        if not self.numero.isdigit():
            raise ValueError("Cédula debe ser numérica")
```

#### Domain Rules
```python
class IdEntidadEsInmutable(ReglaDeNegocio):
    def es_valido(self) -> bool:
        return not hasattr(self.entidad, '_id')
```

### 🏃‍♂️ Flujos de Trabajo de Desarrollo

#### Ejecución Local
```bash
# Desarrollo local - Core Services (Puerto 5000)
flask --app src/alpespartners/api --debug run

# Desarrollo local - BFF Service (Puerto 5001) 
cd src && python -m bff.main

# BFF con Flask directamente
export FLASK_APP=bff.infrastructure.web.app:create_bff_app
flask run --port 5001 --debug

# Stack completo con Pulsar
docker-compose --profile alpespartner up

# Testing con cobertura
coverage run -m pytest && coverage report
```

#### Configuración de Entorno

| Variable | Valor por Defecto | Descripción |
|----------|-------------------|-------------|
| `PULSAR_BROKER_URL` | `pulsar://broker:6650` | URL del broker Pulsar |
| `DB_URL` | `postgresql+psycopg2://partner:partner@postgres:5432/alpespartner` | PostgreSQL |
| `TOPIC_EVENTOS_CAMPANIAS` | `persistent://public/default/eventos.campanias` | Topic Pulsar |
| `PYTHONPATH` | `/src` | Path crítico para imports en Docker |

### 📊 Observabilidad

#### Métricas Implementadas
- **Conteo de requests** (`count`)
- **Errores HTTP 5xx** (`errors`)  
- **Latencias percentiles** (`p50`, `p95`, `p99`)
- **Health checks** (`/health`)

#### Logging
```python
logging.basicConfig(level=logging.DEBUG)
# Stack traces automáticos en errores 500
```

### 🧪 Estrategia de Testing

#### Estructura de Tests
```
tests/
├── unit/
│   ├── modulos/{modulo}/     # Tests por bounded context
│   ├── seedwork/            # Tests del shared kernel
│   └── api/                 # Tests de endpoints
└── integration/             # Tests de integración (futuro)
```

#### Configuración pytest
```toml
[tool.pytest.ini_options]
addopts = ["--import-mode=importlib"]
pythonpath = [".", "src"]
```

### 🚀 Escalabilidad y Rendimiento

#### Estrategias Implementadas
1. **CQRS**: Optimización independiente de reads/writes
2. **Event Sourcing**: Auditabilidad completa y rebuilding
3. **Async Processing**: Comandos procesados de forma asíncrona
4. **Connection Pooling**: `pool_pre_ping=True` en SQLAlchemy
5. **Pulsar**: Broker de alto rendimiento para messaging

#### Puntos de Mejora Identificados
1. **Campanias API**: Actualmente mock, necesita implementación completa
2. **Caching**: No implementado (Redis/Memcached)
3. **Rate Limiting**: No presente
4. **Authentication/Authorization**: Ausente
5. **API Versioning**: No implementado

### 🔍 Análisis de Complejidad

#### Fortalezas Arquitectónicas
✅ **Separación clara de responsabilidades** (DDD)  
✅ **Patrones avanzados bien implementados** (CQRS, Event Sourcing)  
✅ **Event-driven architecture** robusta  
✅ **Observabilidad básica** implementada  
✅ **Testing structure** establecida  

#### Áreas de Atención
⚠️ **Complejidad alta**: Curva de aprendizaje pronunciada  
⚠️ **Over-engineering**: Podría ser excesivo para casos simples  
⚠️ **Documentación**: Falta documentación técnica detallada  
⚠️ **Error Handling**: Manejo de errores inconsistente  
⚠️ **Performance**: Sin optimizaciones específicas  

### 📈 Recomendaciones Técnicas

#### Corto Plazo (1-2 sprints)
1. **Integrar BFF con Docker Compose** para deployment completo
2. **Completar implementación de Campanias** (actualmente mock en BFF)
3. **Testing completo del BFF** (unit + integration tests)
4. **Estandarizar error handling** en todos los endpoints
5. **Implementar logging estructurado** consistente

#### Mediano Plazo (2-4 sprints)  
1. **Añadir autenticación y autorización** (JWT en BFF y services)
2. **Implementar Redis cache** en BFF para optimización
3. **Rate limiting** en APIs y BFF
4. **Metrics avanzadas** (Prometheus/Grafana)
5. **OpenAPI/Swagger** documentation para BFF

#### Largo Plazo (4+ sprints)
1. **API Gateway** para routing centralizado (complementa BFF)
2. **Service mesh** para comunicación inter-servicios
3. **Distributed tracing** (Jaeger/Zipkin)
4. **Performance optimization** y load testing
5. **BFF real-time features** (WebSockets, Server-Sent Events)

---

## 📝 Conclusión

Alpes Partners demuestra una **arquitectura empresarial sólida** con implementación correcta de patrones DDD avanzados. El proyecto incluye ahora:

### 🏗️ Arquitectura Dual
- **Core Microservices** (Puerto 5000): DDD + CQRS + Event Sourcing para lógica de negocio
- **BFF Layer** (Puerto 5001): Hexagonal Architecture para optimización web UI

### ✅ Fortalezas Arquitectónicas
- **Separación clara** entre lógica de dominio (core) y optimización UI (BFF)
- **Patrones avanzados** correctamente implementados (DDD, CQRS, Hexagonal)
- **Event-driven architecture** robusta con Apache Pulsar
- **Escalabilidad horizontal** preparada con arquitectura de microservicios
- **Frontend-optimized APIs** con agregación, paginación y búsqueda integrada

### 🎯 Beneficios del BFF
- **Performance mejorada**: Menos round-trips desde UI
- **Experiencia optimizada**: APIs diseñadas específicamente para web
- **Evolución independiente**: UI puede evolucionar sin afectar core services  
- **Agregación inteligente**: Dashboard con datos pre-calculados
- **Búsqueda unificada**: Un endpoint para buscar en múltiples servicios

El sistema está bien posicionado para escalabilidad futura, con una base sólida tanto para lógica de negocio compleja como para experiencias de usuario optimizadas.