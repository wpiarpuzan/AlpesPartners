# CHANGELOG - Alpes Partners

## [2.0.0] - Backend For Frontend Implementation
### ✨ Added
- **BFF (Backend For Frontend)** con arquitectura hexagonal
  - Puerto HTTP en 5001 para interfaz web
  - Comunicación exclusiva via HTTP REST APIs
  - Dashboard agregado con métricas unificadas
  - Búsqueda unificada cross-module
  - Paginación automática y cacheo de respuestas

### 🏗️ Architecture
- **Hexagonal Architecture** en el BFF
  - Puertos (`domain/ports/`) para abstracciones
  - Adaptadores (`infrastructure/adapters/`) para HTTP
  - Casos de uso (`application/`) para lógica de negocio
  - Controladores (`presentation/`) para endpoints web

### 🌐 HTTP Communication
- Cliente HTTP asíncrono con `aiohttp`
- Manejo de timeouts y reconexión automática  
- Error handling específico para cada tipo de servicio
- Logging detallado para debugging

### 📊 New Endpoints
```
BFF Web UI (Puerto 5001):
├── GET  /api/v1/health          # Health check
├── GET  /api/v1/dashboard       # Métricas agregadas
├── GET  /api/v1/clientes        # Lista paginada
├── GET  /api/v1/pagos           # Lista paginada  
├── GET  /api/v1/campanias       # Lista paginada
└── GET  /api/v1/search?q=...    # Búsqueda unificada
```

### 🛡️ Microservices Compliance
- **Autonomía garantizada**: Sin imports directos entre servicios
- **Comunicación HTTP únicamente**: REST APIs para integración
- **Ciclos de vida independientes**: Cada servicio deployable por separado
- **Resilencia**: Timeouts, reintentos, y circuit breakers

### 🐳 Docker Integration
- Nueva imagen Docker para BFF: `alpespartners/bff`
- Docker Compose actualizado con ambos servicios
- Variables de entorno para configuración HTTP
- Networking entre contenedores

### 📦 Dependencies
- `aiohttp==3.9.1` - Cliente HTTP asíncrono
- `marshmallow==3.20.1` - Validación y serialización
- Mantenimiento de compatibilidad con AlpesPartners Core existente

### 🧪 Testing
- Script `test_bff_http.py` para validación de comunicación
- Tests de health check para ambos servicios
- Validación de endpoints y timeouts
- Comparación BFF vs Backend directo

### 📚 Documentation
- README actualizado con arquitectura completa
- Copilot instructions con patrones HTTP
- Diagramas de comunicación entre servicios
- Guías de ejecución local y Docker

### ⚡ Performance
- Cacheo inteligente de respuestas HTTP
- Pool de conexiones HTTP reutilizable
- Paginación automática para grandes datasets
- Timeouts configurables por operación

---

## [1.0.0] - AlpesPartners Core
### 🎯 Initial Implementation  
- **Domain-Driven Design** con bounded contexts
- **CQRS** para separación comando/query
- **Event Sourcing** con Apache Pulsar
- **Módulos**: Campañas, Cliente, Pagos
- **Seedwork** compartido entre módulos
- **Unit of Work** para transacciones
- **PostgreSQL** como persistence store

### 📡 Event Architecture
- Eventos de dominio e integración
- Consumidores funcionales (Pulsar)
- Publishers orientados a objetos
- Event Store para sourcing

### 🔧 Infrastructure
- Flask API con blueprints por módulo
- Docker Compose con Pulsar y PostgreSQL
- Unit tests con coverage reporting
- Configuración via environment variables