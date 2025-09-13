# Alpes Partners - AI Coding Assistant Guide

## Architecture Overview
This is a **Domain-Driven Design (DDD)** microservices system with **CQRS** and **Event Sourcing** patterns. The architecture uses **Pulsar** as the event broker and **PostgreSQL** for persistence.

### Core Structure
- **`src/alpespartners/seedwork/`** - Shared kernel with base classes and patterns
- **`src/alpespartners/modulos/`** - Bounded contexts: `campanias`, `cliente`, `pagos`
- **`src/alpespartners/api/`** - REST API endpoints (Flask blueprints)
- **`src/alpespartners/config/`** - Database and UoW configuration

## Key Patterns & Conventions

### 1. Seedwork Foundation
All domain entities extend from `seedwork/dominio/entidades.py`:
```python
from alpespartners.seedwork.dominio.entidades import Entidad, AgregacionRaiz
```
- Use `AgregacionRaiz` for entities that generate domain events
- Always call `agregar_evento()` when domain state changes

### 2. CQRS Implementation
Commands and queries are strictly separated using `@singledispatch`:
```python
# In aplicacion/comandos/
@ejecutar_commando.register
def comando_crear_campania(comando: CrearCampania):
    # Handle command

# In aplicacion/queries/
@ejecutar_query.register  
def query_obtener_campania(query: ObtenerCampania):
    # Handle query
```

### 3. Unit of Work Pattern
**CRITICAL**: Always use UoW for transactional operations:
```python
from alpespartners.seedwork.infraestructura.uow import UnidadTrabajoPuerto

# Register operations, don't execute directly
UnidadTrabajoPuerto.registrar_batch(repo.agregar, campania)
UnidadTrabajoPuerto.commit()  # Triggers domain & integration events
```

### 4. Event Sourcing
Each module has `infraestructura/event_store.py`:
- Use `append_event(aggregate_id, type_, data)` to store events
- Events follow naming: `CampaniaCreada.v1`, `PagoConfirmado.v1`
- All events must have `schemaVersion` and `to_dict()` method

### 5. Cross-Module Communication
Modules communicate via Pulsar topics:
- **Commands**: `comandos.{modulo}` (e.g., `comandos.campanias`)
- **Events**: `eventos.{modulo}` (e.g., `eventos.pagos`)
- Use `infraestructura/consumidores.py` for listening
- Use `infraestructura/publisher.py` for publishing

## Development Workflow

### Running the Application
```bash
# Local development
flask --app src/alpespartners/api --debug run

# With Docker (full stack with Pulsar)
docker-compose --profile alpespartner up

# Tests with coverage
coverage run -m pytest && coverage report
```

### Module Structure Template
When adding new bounded contexts, follow this structure:
```
modulos/{nombre}/
├── aplicacion/
│   ├── comandos/     # Command handlers with @ejecutar_commando.register
│   ├── queries/      # Query handlers with @ejecutar_query.register  
│   ├── dto.py        # Data transfer objects
│   └── mapeadores.py # Domain ↔ DTO mapping
├── dominio/
│   ├── entidades.py  # Aggregate roots extending AgregacionRaiz
│   ├── eventos.py    # Domain events with to_dict() method
│   └── repositorios.py # Repository interfaces
└── infraestructura/
    ├── consumidores.py   # Pulsar event consumers (functional style)
    ├── publisher.py      # Event publishing (OOP style)
    ├── repos.py         # Repository implementations
    └── event_store.py   # Event sourcing operations
```

### API Conventions
Flask blueprints in `api/{modulo}.py`:
- POST `/comandos/{accion}` - Returns 202 for async commands
- GET `/{id}` or `/queries/{accion}` - Returns 200 for queries
- Use `request.get_json()` and `jsonify()` consistently

### Testing Patterns
Tests in `tests/unit/{modulo}/`:
- Test domain logic without infrastructure dependencies
- Mock external services (Pulsar, database)
- Use `pytest` with coverage reporting via `coverage run -m pytest`

## Environment Configuration
Key environment variables for Docker/production:
- `PULSAR_BROKER_URL=pulsar://broker:6650`
- `DB_URL=postgresql+psycopg2://partner:partner@postgres:5432/alpespartner`
- `TOPIC_EVENTOS_CAMPANIAS=persistent://public/default/eventos.campanias`
- `PYTHONPATH=/src` (critical for Docker imports)

## Critical Implementation Notes
- **Never bypass UoW**: Direct repository calls skip event publishing
- **Event naming**: Use `{Entity}{Action}.v{version}` format consistently
- **Functional consumers**: Event consumers use functional programming style
- **OOP publishers**: Event publishers use object-oriented style
- **Schema versioning**: Always include `schemaVersion` in event payloads
- **Aggregate IDs**: Use string IDs, not UUIDs for cross-module references