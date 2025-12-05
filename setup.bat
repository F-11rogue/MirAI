@echo off
REM Script de inicio rápido para el Agente de IA (Windows)
REM Quick start script for AI Agent (Windows)

echo ==========================================
echo 🤖 MirAI - Configuración Inicial
echo ==========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no está instalado
    echo Por favor instala Python 3.8 o superior
    pause
    exit /b 1
)

python --version
echo.

REM Cambiar al directorio del agente
if not exist "agente-ia" (
    echo ❌ Error: directorio agente-ia no encontrado
    echo Asegúrate de ejecutar este script desde el directorio raíz del proyecto
    pause
    exit /b 1
)

cd agente-ia

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
    echo ✓ Entorno virtual creado
    echo.
)

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo 📥 Instalando dependencias...
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q

echo ✓ Dependencias instaladas
echo.

REM Copiar .env.example si no existe .env
if not exist ".env" (
    echo 📝 Creando archivo .env...
    copy .env.example .env
    echo ✓ Archivo .env creado
    echo ⚠️  IMPORTANTE: Edita .env con tus API keys
    echo.
)

REM Generar datos de ejemplo si no existen
if not exist "data\training\example_conversational.json" (
    echo 📊 Generando datos de ejemplo...
    python src\data_processor.py
    echo ✓ Datos de ejemplo creados
    echo.
)

echo ==========================================
echo ✅ Configuración completada!
echo ==========================================
echo.
echo Próximos pasos:
echo.
echo 1. Edita el archivo .env con tus API keys
echo    notepad agente-ia\.env
echo.
echo 2. Prueba el agente clasificador (no requiere API key):
echo    cd agente-ia
echo    venv\Scripts\activate
echo    python src\train.py --agent-type classifier
echo    python src\inference.py --interactive
echo.
echo 3. Lee la guía completa:
echo    type GUIA_AGENTE_IA.md
echo.
echo 4. Explora el notebook interactivo:
echo    jupyter notebook agente-ia\notebooks\exploracion.ipynb
echo.
echo ¡Buena suerte con tu agente de IA! 🚀
echo.
pause
