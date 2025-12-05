# Mi Agente IA - Sistema de Entrenamiento

Este directorio contiene todo lo necesario para crear, entrenar y desplegar tu agente de inteligencia artificial.

## 🚀 Inicio Rápido

### 1. Configuración del Entorno

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus claves API
nano .env
```

### 3. Preparar Datos de Entrenamiento

```bash
# Los datos van en data/raw/
# Por ejemplo:
data/raw/conversaciones.json
data/raw/preguntas_frecuentes.csv
```

### 4. Entrenar el Agente

```bash
# Entrenar con configuración por defecto
python src/train.py

# O con configuración personalizada
python src/train.py --config config/agent_config.yaml
```

### 5. Probar el Agente

```bash
# Modo interactivo
python src/inference.py --interactive

# O procesar un archivo
python src/inference.py --input test_data.txt
```

## 📁 Estructura del Proyecto

```
agente-ia/
├── README.md                  # Este archivo
├── requirements.txt           # Dependencias Python
├── .env.example              # Plantilla de variables de entorno
├── .gitignore               # Archivos a ignorar en Git
│
├── config/                   # Configuraciones
│   ├── agent_config.yaml    # Configuración del agente
│   └── model_config.yaml    # Configuración del modelo
│
├── data/                     # Datos
│   ├── raw/                 # Datos sin procesar
│   ├── processed/           # Datos procesados
│   └── training/            # Datos listos para entrenar
│
├── src/                      # Código fuente
│   ├── __init__.py
│   ├── agent.py             # Clase principal del agente
│   ├── train.py             # Script de entrenamiento
│   ├── inference.py         # Script para usar el agente
│   ├── data_processor.py    # Procesamiento de datos
│   └── utils.py             # Utilidades
│
├── notebooks/               # Jupyter notebooks
│   └── exploracion.ipynb   # Exploración de datos
│
├── tests/                   # Tests unitarios
│   └── test_agent.py       # Tests del agente
│
└── models/                  # Modelos entrenados
    └── trained/             # Modelos guardados
```

## 🎯 Tipos de Agentes Incluidos

### 1. Agente Conversacional (LLM-based)
- Usa OpenAI GPT o modelos similares
- Ideal para chatbots y asistentes
- Archivo: `src/agent.py` (ConversationalAgent)

### 2. Agente Clasificador
- Usa scikit-learn o transformers
- Ideal para categorización
- Archivo: `src/agent.py` (ClassifierAgent)

### 3. Agente Personalizado
- Plantilla base para crear tu propio agente
- Hereda de BaseAgent
- Archivo: `src/agent.py` (CustomAgent)

## 📊 Formatos de Datos Soportados

### Para Agentes Conversacionales:
```json
[
  {
    "user": "¿Cuál es el horario?",
    "assistant": "Nuestro horario es de lunes a sábado, 9:00 AM - 6:00 PM",
    "context": "info_general"
  }
]
```

### Para Agentes Clasificadores:
```csv
texto,categoria
"Necesito agendar una cita",solicitud_cita
"¿Cuánto cuesta el servicio?",consulta_precio
```

## 🔧 Configuración

### agent_config.yaml
```yaml
agent:
  name: "MiAgente"
  type: "conversational"  # conversational, classifier, custom
  version: "1.0"
  
training:
  batch_size: 16
  epochs: 10
  learning_rate: 0.001
  
model:
  provider: "openai"  # openai, huggingface, local
  model_name: "gpt-3.5-turbo"
```

## 🧪 Ejecutar Tests

```bash
# Todos los tests
pytest tests/

# Test específico
pytest tests/test_agent.py

# Con cobertura
pytest --cov=src tests/
```

## 📈 Métricas de Evaluación

El sistema registra automáticamente:
- Precisión (Accuracy)
- Recall
- F1-Score
- Tiempo de respuesta
- Uso de tokens (para LLMs)

Ver métricas en: `models/trained/metrics.json`

## 🌐 Despliegue

### Opción 1: API REST (FastAPI)
```bash
cd src
uvicorn api:app --reload
```

### Opción 2: Streamlit Web App
```bash
streamlit run src/webapp.py
```

### Opción 3: Docker
```bash
docker build -t mi-agente .
docker run -p 8000:8000 mi-agente
```

## 💾 Guardar y Cargar Modelos

```python
from src.agent import ConversationalAgent

# Entrenar y guardar
agent = ConversationalAgent()
agent.train(data)
agent.save("models/trained/mi_modelo")

# Cargar modelo entrenado
agent = ConversationalAgent.load("models/trained/mi_modelo")
```

## 🔍 Monitoreo y Logging

Los logs se guardan en:
- `logs/training.log` - Logs de entrenamiento
- `logs/inference.log` - Logs de inferencia
- `logs/errors.log` - Errores

## 🤝 Mejores Prácticas

1. **Versionamiento**: Usa Git para versionar tu código y datos
2. **Experimentación**: Prueba diferentes hiperparámetros
3. **Validación**: Siempre valida con datos no vistos
4. **Documentación**: Documenta tus experimentos
5. **Backup**: Guarda copias de tus mejores modelos

## 📚 Recursos y Documentación

- [Documentación de LangChain](https://python.langchain.com/)
- [Guía de OpenAI](https://platform.openai.com/docs/)
- [Scikit-learn Docs](https://scikit-learn.org/)
- [Tutorial de PyTorch](https://pytorch.org/tutorials/)

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Error: "API Key not found"
```bash
# Asegúrate de tener .env configurado
cp .env.example .env
# Edita .env con tus claves
```

### Modelo no converge
- Reduce learning_rate
- Aumenta epochs
- Verifica calidad de datos

## 📞 Soporte

¿Tienes preguntas? 
- Abre un issue en GitHub
- Consulta la documentación principal en `/GUIA_AGENTE_IA.md`
- Revisa los ejemplos en `notebooks/`

---

**¡Feliz entrenamiento! 🤖**
