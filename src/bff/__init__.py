"""
Backend For Frontend (BFF) - Web UI Module

Este módulo implementa un Backend For Frontend específico para interfaces web,
utilizando arquitectura hexagonal para desacoplar la lógica de negocio de los
detalles de infraestructura.

Arquitectura Hexagonal:
- Domain: Lógica de negocio y reglas específicas del BFF
- Application: Casos de uso y orquestación
- Infrastructure: Adaptadores para servicios externos, web frameworks, etc.
"""

__version__ = "1.0.0"