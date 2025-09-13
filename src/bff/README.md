# BFF Web UI - Backend For Frontend

## Descripción
Backend For Frontend optimizado para interfaces web del sistema Alpes Partners. Implementa **arquitectura hexagonal** con comunicación HTTP a microservicios, siguiendo principios de **autonomía y desacoplamiento**.

## ✅ Arquitectura Corregida

### Principios Aplicados
- 🚫 **Sin imports directos** a módulos alpespartners
- 🌐 **Comunicación HTTP exclusiva** con APIs REST
- 🔄 **Ciclo de vida autónomo** del BFF
- 📦 **Desacoplamiento total** entre servicios

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

### Optimizaciones BFF
- ✅ **Agregación de datos**: Dashboard combina múltiples servicios
- ✅ **Paginación inteligente**: Metadata completa para UI
- ✅ **Búsqueda unificada**: Un endpoint para múltiples servicios
- ✅ **Vista detallada**: Cliente + pagos + campañas en una request
- ✅ **Cache en memoria**: Reduce llamadas HTTP repetitivas
- ✅ **Manejo de errores**: Fallback a datos mock si servicios fallan

## 🛠️ Implementación HTTP

### Cliente HTTP Base
```python
# bff/infrastructure/http_client.py
class AlpesPartnersHttpClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url  # http://localhost:5000
        
    async def get(self, endpoint: str) -> Dict[str, Any]:
        # GET http://localhost:5000/cliente/123
        
    async def post(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        # POST http://localhost:5000/cliente/registrar
```

### Adaptadores HTTP
```python
# bff/infrastructure/adapters/cliente_adapter.py
class ClienteServiceAdapter:
    def __init__(self, http_client: ClienteServiceHttpClient):
        self.http_client = http_client  # 🚫 No imports directos
    
    async def obtener_cliente(self, id: str):
        # HTTP GET /cliente/{id} en lugar de import directo
        data = await self.http_client.obtener_cliente(id)
```

## 🔄 Ventajas de la Nueva Implementación

### ✅ Microservicios Reales
- **Autonomía**: BFF tiene su propio ciclo de vida
- **Escalabilidad**: Servicios pueden escalarse independientemente  
- **Despliegue**: BFF y core services en containers separados
- **Mantenibilidad**: Cambios en core services no afectan BFF

### ✅ Comunicación HTTP
- **Estándar**: REST APIs como interfaz única entre servicios
- **Monitoreo**: Requests HTTP se pueden interceptar y monitorear
- **Load Balancing**: Múltiples instancias de servicios backend
- **Resilencia**: Timeouts, reintentos, circuit breakers

### ✅ Desarrollo
- **Testing**: BFF se puede testear con mocks HTTP
- **Debug**: Tráfico HTTP es visible en logs/herramientas
- **Documentación**: APIs REST auto-documentadas

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

## 🧪 Testing

### Unit Tests
```bash
# Tests de adaptadores HTTP (con mocks)
pytest tests/bff/test_http_adapters.py

# Tests de casos de uso
pytest tests/bff/test_use_cases.py
```

### Integration Tests
```bash
# Tests con servicios reales ejecutándose
pytest tests/integration/test_bff_integration.py
```

## 📈 Monitoreo y Observabilidad

### Health Check Avanzado
```json
{
  "status": "healthy",
  "services": {
    "cliente_service": {"status": "up", "response_time_ms": 45},
    "pagos_service": {"status": "up", "response_time_ms": 32},
    "campanias_service": {"status": "degraded", "response_time_ms": 1200}
  }
}
```

### Logs HTTP
- Request/Response logging
- Error tracking con stack traces
- Performance metrics por endpoint
- Circuit breaker status

## 🚀 Próximos Pasos

### Inmediatos
1. ✅ **Completado**: Implementación HTTP sin imports directos
2. 🔧 **Testing**: Suite completa de tests unitarios e integración
3. 🐳 **Docker**: Dockerfile específico para BFF
4. 📊 **Monitoring**: Métricas detalladas de HTTP requests

### Mejoras
1. 🔄 **Circuit Breaker**: Resilencia ante fallos de servicios
2. ⚡ **Redis Cache**: Cache distribuido para múltiples instancias BFF
3. 🔒 **JWT Auth**: Autenticación unificada
4. 📝 **OpenAPI**: Documentación automática con Swagger