# BFF Web UI - Backend For Frontend

## Descripción
Backend For Frontend optimizado para interfaces web del sistema Alpes Partners. Implementa arquitectura hexagonal con las mejores prácticas de desarrollo.

## Arquitectura

### Hexagonal Architecture
```
📁 bff/
├── 🏛️ domain/           # Dominio del BFF
│   ├── models/          # Modelos específicos para UI web
│   └── exceptions/      # Excepciones del dominio
├── 🎯 application/      # Casos de uso y puertos
│   ├── use_cases/       # Casos de uso específicos para web
│   └── ports/           # Interfaces (puertos)
└── 🔧 infrastructure/   # Adaptadores e infraestructura
    ├── adapters/        # Adaptadores para servicios backend
    ├── web/            # Framework web (Flask)
    └── config.py       # Configuración e inyección de dependencias
```

### Patrones Implementados
- ✅ **Hexagonal Architecture** (Ports & Adapters)
- ✅ **Dependency Injection** con contenedor DI
- ✅ **CQRS** para separar lecturas y escrituras
- ✅ **Repository Pattern** via adaptadores
- ✅ **Use Case Pattern** para lógica de negocio
- ✅ **DTO Pattern** para transferencia de datos

## Endpoints API

### Dashboard
- `GET /api/v1/dashboard` - Datos agregados del dashboard

### Clientes
- `GET /api/v1/clientes` - Lista clientes (paginado)
- `GET /api/v1/clientes/{id}` - Detalle de cliente
- `POST /api/v1/clientes` - Crear cliente

### Pagos
- `GET /api/v1/pagos` - Lista pagos (paginado)
- `GET /api/v1/pagos/{id}` - Detalle de pago

### Campañas
- `GET /api/v1/campanias` - Lista campañas (paginado)

### Búsqueda
- `GET /api/v1/search?q={term}` - Búsqueda integrada

### Health
- `GET /api/v1/health` - Health check

## Ejecutar BFF

### Desarrollo
```bash
# Desde la raíz del proyecto
cd src
python -m bff.main

# O usando Flask directamente
export FLASK_APP=bff.infrastructure.web.app:create_bff_app
flask run --port 5001
```

### Variables de Entorno
- `BFF_HOST` - Host del servidor (default: 0.0.0.0)
- `BFF_PORT` - Puerto del servidor (default: 5001)
- `BFF_DEBUG` - Modo debug (default: False)
- `BFF_SECRET_KEY` - Clave secreta para Flask

### Con Docker
```bash
# Dockerfile para BFF (agregar al proyecto)
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
EXPOSE 5001

CMD ["python", "-m", "bff.main"]
```

## Características

### Optimizaciones para UI Web
- ✅ **Paginación** en todos los listados
- ✅ **Búsqueda integrada** en múltiples servicios
- ✅ **Agregación de datos** (Dashboard)
- ✅ **Vistas compuestas** (Cliente con pagos/campañas)
- ✅ **Cache en memoria** para rendimiento
- ✅ **Validación robusta** con Marshmallow

### Integraciones
- 🔗 **Servicio Clientes** - Via adaptador directo
- 🔗 **Servicio Pagos** - Via adaptador directo  
- 🔗 **Servicio Campañas** - Via adaptador (mock)
- 📊 **Logging estructurado**
- ⚡ **Cache de datos**

## Testing

```bash
# Unit tests (implementar)
pytest tests/bff/

# Integration tests
pytest tests/integration/bff/
```

## Monitoreo
- Logs estructurados en `logs/bff.log`
- Health check endpoint
- Request/Response logging en modo debug

## Próximos Pasos
1. 🔒 Implementar autenticación JWT
2. 📊 Métricas con Prometheus
3. 🔄 Rate limiting
4. 📝 OpenAPI/Swagger documentation
5. 🧪 Suite de tests completa