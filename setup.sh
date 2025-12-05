#!/bin/bash
# Script de inicio rápido para el Agente de IA
# Quick start script for AI Agent

echo "=========================================="
echo "🤖 MirAI - Configuración Inicial"
echo "=========================================="
echo ""

# Verificar Python
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null
then
    echo "❌ Python no está instalado"
    echo "Por favor instala Python 3.8 o superior"
    exit 1
fi

# Usar python3 si está disponible
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

echo "✓ Python encontrado: $($PYTHON_CMD --version)"
echo ""

# Cambiar al directorio del agente
cd agente-ia

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    $PYTHON_CMD -m venv venv
    echo "✓ Entorno virtual creado"
    echo ""
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "✓ Dependencias instaladas"
echo ""

# Copiar .env.example si no existe .env
if [ ! -f ".env" ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
    echo "✓ Archivo .env creado"
    echo "⚠️  IMPORTANTE: Edita .env con tus API keys"
    echo ""
fi

# Generar datos de ejemplo si no existen
if [ ! -f "data/training/example_conversational.json" ]; then
    echo "📊 Generando datos de ejemplo..."
    $PYTHON_CMD src/data_processor.py
    echo "✓ Datos de ejemplo creados"
    echo ""
fi

echo "=========================================="
echo "✅ Configuración completada!"
echo "=========================================="
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Edita el archivo .env con tus API keys"
echo "   nano agente-ia/.env"
echo ""
echo "2. Prueba el agente clasificador (no requiere API key):"
echo "   cd agente-ia"
echo "   source venv/bin/activate"
echo "   python src/train.py --agent-type classifier"
echo "   python src/inference.py --interactive"
echo ""
echo "3. Lee la guía completa:"
echo "   cat GUIA_AGENTE_IA.md"
echo ""
echo "4. Explora el notebook interactivo:"
echo "   jupyter notebook agente-ia/notebooks/exploracion.ipynb"
echo ""
echo "¡Buena suerte con tu agente de IA! 🚀"
echo ""
