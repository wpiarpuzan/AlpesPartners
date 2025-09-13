#!/usr/bin/env python3
"""
Script de prueba para verificar comunicación HTTP del BFF

Este script verifica que el BFF se comunique correctamente con los 
microservicios de Alpes Partners via HTTP REST APIs.
"""

import asyncio
import json
import os
import sys
import aiohttp
from datetime import datetime

# Configuración
BFF_BASE_URL = "http://localhost:5001"
ALPESPARTNERS_BASE_URL = "http://localhost:5000"

async def check_service_health(url: str, service_name: str):
    """Verifica el estado de un servicio"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    print(f"✅ {service_name}: OK (HTTP {response.status})")
                    return True
                else:
                    print(f"⚠️  {service_name}: HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"❌ {service_name}: Error - {str(e)}")
        return False

async def test_bff_endpoints():
    """Prueba los endpoints principales del BFF"""
    endpoints = [
        ("Health Check", "GET", "/api/v1/health"),
        ("Dashboard", "GET", "/api/v1/dashboard"),
        ("Lista Clientes", "GET", "/api/v1/clientes?page=1&per_page=5"),
        ("Lista Pagos", "GET", "/api/v1/pagos?page=1&per_page=5"),
        ("Lista Campañas", "GET", "/api/v1/campanias?page=1&per_page=5"),
        ("Búsqueda", "GET", "/api/v1/search?q=test"),
    ]
    
    print("\n🔍 Probando endpoints del BFF...")
    
    async with aiohttp.ClientSession() as session:
        for name, method, endpoint in endpoints:
            try:
                url = f"{BFF_BASE_URL}{endpoint}"
                async with session.request(method, url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    status = response.status
                    response_text = await response.text()
                    
                    if status == 200:
                        try:
                            json.loads(response_text)  # Validate JSON
                            print(f"✅ {name}: OK (HTTP {status}) - {len(response_text)} chars")
                        except json.JSONDecodeError:
                            print(f"⚠️  {name}: OK pero respuesta no es JSON válido")
                    else:
                        print(f"❌ {name}: HTTP {status}")
                        print(f"   Response: {response_text[:100]}...")
                        
            except Exception as e:
                print(f"❌ {name}: Error - {str(e)}")

async def test_direct_backend_communication():
    """Prueba comunicación directa con servicios backend"""
    print("\n🌐 Probando comunicación directa con AlpesPartners...")
    
    # Test crear cliente
    cliente_data = {
        "id": f"test-client-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "nombre": "Cliente Test HTTP",
        "email": f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        "cedula": "12345678",
        "fecha_nacimiento": "1990-01-01T00:00:00"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # Crear cliente via backend directo
            async with session.post(
                f"{ALPESPARTNERS_BASE_URL}/cliente/registrar",
                json=cliente_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status in [200, 201]:
                    response_data = await response.json()
                    cliente_id = response_data.get('id')
                    print(f"✅ Cliente creado directamente: {cliente_id}")
                    
                    # Obtener cliente via backend directo
                    async with session.get(f"{ALPESPARTNERS_BASE_URL}/cliente/{cliente_id}") as get_response:
                        if get_response.status == 200:
                            print("✅ Cliente obtenido directamente: OK")
                        else:
                            print(f"⚠️  Error obteniendo cliente: HTTP {get_response.status}")
                else:
                    print(f"❌ Error creando cliente: HTTP {response.status}")
                    
        except Exception as e:
            print(f"❌ Error en comunicación backend: {str(e)}")

def test_bff_vs_backend_comparison():
    """Compara respuestas del BFF vs Backend directo"""
    print("\n⚖️  Comparando BFF vs Backend directo...")
    
    # Esta prueba requiere que ambos servicios estén ejecutándose
    # y que existan datos de prueba

async def main():
    """Función principal"""
    print("🧪 Test de Comunicación HTTP - Alpes Partners BFF")
    print("="*50)
    
    # Verificar servicios
    print("\n📡 Verificando servicios...")
    bff_ok = await check_service_health(BFF_BASE_URL, "BFF Web UI (5001)")
    backend_ok = await check_service_health(ALPESPARTNERS_BASE_URL, "AlpesPartners Core (5000)")
    
    if not bff_ok and not backend_ok:
        print("\n❌ Ningún servicio está disponible. Asegúrate de que estén ejecutándose:")
        print("   • BFF: python -m bff.main")
        print("   • Backend: flask --app alpespartners/api --debug run")
        return 1
    
    # Probar BFF si está disponible
    if bff_ok:
        await test_bff_endpoints()
    
    # Probar backend directo si está disponible
    if backend_ok:
        await test_direct_backend_communication()
    
    print("\n✅ Tests completados!")
    print("\n💡 Para ejecutar ambos servicios:")
    print("   Terminal 1: cd src && flask --app alpespartners/api --debug run")
    print("   Terminal 2: cd src && python -m bff.main")
    
    return 0

if __name__ == "__main__":
    # Verificar dependencias
    try:
        import aiohttp
    except ImportError:
        print("❌ Error: aiohttp no está instalado")
        print("   Instalar con: pip install aiohttp")
        sys.exit(1)
    
    # Ejecutar tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)