#!/bin/bash

set -e

echo "=== Configuración del entorno de umai-api ==="

# Actualizar repositorios e instalar pip y venv
echo "Instalando dependencias del sistema (pip y venv)..."
sudo apt update && sudo apt install python3-pip python3-venv -y

# Crear el entorno virtual llamado 'venv'
echo "Creando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Entorno virtual creado"
else
    echo "✓ El entorno virtual ya existe"
fi

# Activar el entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate

# Verificar que el entorno virtual está activo
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Error: No se pudo activar el entorno virtual"
    exit 1
fi
echo "✓ Entorno virtual activado: $VIRTUAL_ENV"

# Instalar dependencias
echo "Instalando dependencias desde requirements.txt..."
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

# Mostrar información final
echo ""
echo "=== ✓ Configuración completada ==="
echo "Para activar el entorno virtual en futuras sesiones, ejecuta:"
echo "    source venv/bin/activate"
echo ""
echo "Para desactivar el entorno virtual, ejecuta:"
echo "    deactivate"
echo ""
echo "Iniciando la aplicación..."
echo ""

# Levantar la aplicación
python3 -m app