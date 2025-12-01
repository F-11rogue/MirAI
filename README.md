# MirAI - Reproductor de Música en Python 🎵

Un reproductor de música simple y elegante con interfaz gráfica creado en Python.

## Características

- ▶️ **Reproducir/Pausar/Detener** - Control completo de reproducción
- ⏮️⏭️ **Navegación** - Anterior y siguiente canción
- 🔊 **Control de volumen** - Slider ajustable de 0% a 100%
- 📋 **Lista de reproducción** - Agregar, eliminar y limpiar canciones
- 🎨 **Interfaz moderna** - Diseño oscuro y atractivo
- 🎵 **Múltiples formatos** - Soporte para MP3, WAV y OGG

## Requisitos

- Python 3.7 o superior
- pygame

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/F-11rogue/MirAI.git
cd MirAI
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

Ejecuta el reproductor con:
```bash
python reproductor_musica.py
```

### Controles

| Botón | Función |
|-------|---------|
| ⏮ | Canción anterior |
| ▶ | Reproducir |
| ⏸ | Pausar |
| ⏹ | Detener |
| ⏭ | Siguiente canción |

### Gestión de Lista de Reproducción

- **Agregar**: Haz clic en "➕ Agregar" para seleccionar archivos de audio
- **Eliminar**: Selecciona una canción y haz clic en "➖ Eliminar"
- **Limpiar**: Haz clic en "🗑 Limpiar" para vaciar toda la lista
- **Doble clic**: Reproduce la canción seleccionada directamente

## Estructura del Proyecto

```
MirAI/
├── README.md              # Documentación
├── requirements.txt       # Dependencias
└── reproductor_musica.py  # Código principal del reproductor
```

## Licencia

Este proyecto está disponible para uso libre.