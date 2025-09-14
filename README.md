
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

