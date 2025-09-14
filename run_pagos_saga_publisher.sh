#!/bin/bash
# Script para ejecutar el publisher/orquestador de pagos y mostrar los logs en tiempo real

source .venv/bin/activate
python src/alpespartners/modulos/pagos/infraestructura/saga_publisher.py
