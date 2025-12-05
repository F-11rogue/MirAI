"""
Utilidades y funciones de ayuda para el agente de IA
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


def measure_time(func):
    """
    Decorador para medir el tiempo de ejecución de una función.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed = end_time - start_time
        logger.info(f"{func.__name__} completado en {elapsed:.2f} segundos")
        return result
    return wrapper


def ensure_dir(directory: str):
    """
    Asegura que un directorio existe, si no, lo crea.
    
    Args:
        directory: Ruta del directorio
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Directorio creado: {directory}")


def save_json(data: Any, file_path: str, indent: int = 2):
    """
    Guarda datos en formato JSON.
    
    Args:
        data: Datos a guardar
        file_path: Ruta del archivo
        indent: Indentación del JSON
    """
    ensure_dir(os.path.dirname(file_path))
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    
    logger.debug(f"JSON guardado en: {file_path}")


def load_json(file_path: str) -> Any:
    """
    Carga datos desde un archivo JSON.
    
    Args:
        file_path: Ruta del archivo
    
    Returns:
        Datos cargados
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.debug(f"JSON cargado desde: {file_path}")
    return data


def get_timestamp() -> str:
    """
    Obtiene un timestamp formateado.
    
    Returns:
        Timestamp en formato ISO 8601
    """
    return datetime.now().isoformat()


def format_timestamp(timestamp: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Formatea un timestamp ISO a un formato legible.
    
    Args:
        timestamp: Timestamp en formato ISO
        format_str: Formato deseado
    
    Returns:
        Timestamp formateado
    """
    dt = datetime.fromisoformat(timestamp)
    return dt.strftime(format_str)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Trunca un texto a una longitud máxima.
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a agregar si se trunca
    
    Returns:
        Texto truncado
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Estima la cantidad de tokens en un texto.
    Usa una aproximación simple (palabras * 1.3)
    
    Para conteo preciso, instala tiktoken:
    pip install tiktoken
    
    Args:
        text: Texto a contar
        model: Modelo para el conteo (usado con tiktoken)
    
    Returns:
        Número estimado de tokens
    """
    try:
        import tiktoken
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except ImportError:
        # Aproximación simple si tiktoken no está instalado
        words = len(text.split())
        return int(words * 1.3)


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "gpt-3.5-turbo"
) -> float:
    """
    Estima el costo de una llamada al API.
    
    Args:
        input_tokens: Número de tokens de entrada
        output_tokens: Número de tokens de salida
        model: Modelo usado
    
    Returns:
        Costo estimado en USD
    """
    # Precios por 1K tokens (actualizar según precios actuales)
    pricing = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    }
    
    if model not in pricing:
        logger.warning(f"Modelo {model} no encontrado en tabla de precios")
        return 0.0
    
    input_cost = (input_tokens / 1000) * pricing[model]["input"]
    output_cost = (output_tokens / 1000) * pricing[model]["output"]
    
    return input_cost + output_cost


def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """
    Decorador para reintentar una función si falla.
    
    Args:
        max_retries: Número máximo de reintentos
        delay: Tiempo de espera entre reintentos (segundos)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        raise
                    
                    logger.warning(
                        f"Intento {attempt + 1}/{max_retries} falló: {e}. "
                        f"Reintentando en {delay}s..."
                    )
                    time.sleep(delay)
            
            # Si llegamos aquí, todos los reintentos fallaron
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza un nombre de archivo removiendo caracteres no válidos.
    
    Args:
        filename: Nombre de archivo original
    
    Returns:
        Nombre de archivo sanitizado
    """
    import re
    
    # Remover caracteres no válidos
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Limitar longitud
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename


def load_env_vars(env_file: str = ".env"):
    """
    Carga variables de entorno desde un archivo .env
    
    Args:
        env_file: Ruta al archivo .env
    """
    try:
        from dotenv import load_dotenv
        
        if os.path.exists(env_file):
            load_dotenv(env_file)
            logger.info(f"Variables de entorno cargadas desde: {env_file}")
        else:
            logger.warning(f"Archivo .env no encontrado: {env_file}")
    except ImportError:
        logger.warning("python-dotenv no instalado. Instala con: pip install python-dotenv")
        logger.info("Las variables de entorno del sistema serán usadas.")


def get_memory_usage() -> Dict[str, float]:
    """
    Obtiene información sobre el uso de memoria.
    
    Returns:
        Dict con información de memoria en MB
    """
    try:
        import psutil
        
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
        }
    except ImportError:
        logger.warning("psutil no instalado. Instala con: pip install psutil")
        return {
            'rss_mb': 0.0,
            'vms_mb': 0.0,
        }


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_str: Optional[str] = None
):
    """
    Configura el sistema de logging.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        log_file: Ruta opcional para guardar logs
        format_str: Formato personalizado de logs
    """
    if format_str is None:
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Nivel de logging
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configurar
    handlers = [logging.StreamHandler()]
    
    if log_file:
        ensure_dir(os.path.dirname(log_file))
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=log_level,
        format=format_str,
        handlers=handlers
    )
    
    logger.info(f"Logging configurado - Nivel: {level}")


def validate_api_key(provider: str = "openai") -> bool:
    """
    Valida que exista una API key en las variables de entorno.
    
    Args:
        provider: Proveedor del API (openai, anthropic, etc.)
    
    Returns:
        True si la API key existe, False en caso contrario
    """
    env_var_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "huggingface": "HUGGINGFACE_API_TOKEN",
    }
    
    env_var = env_var_map.get(provider.lower())
    
    if not env_var:
        logger.warning(f"Proveedor desconocido: {provider}")
        return False
    
    api_key = os.getenv(env_var)
    
    if not api_key:
        logger.error(f"API key no encontrada: {env_var}")
        logger.info(f"Por favor, configura {env_var} en tu archivo .env")
        return False
    
    logger.info(f"API key encontrada para {provider}")
    return True


def print_banner(text: str, char: str = "=", width: int = 60):
    """
    Imprime un banner decorativo.
    
    Args:
        text: Texto a mostrar
        char: Carácter para el borde
        width: Ancho del banner
    """
    border = char * width
    padding = (width - len(text) - 2) // 2
    
    print(f"\n{border}")
    print(f"{char}{' ' * padding}{text}{' ' * padding}{char}")
    print(f"{border}\n")


if __name__ == "__main__":
    # Tests básicos
    print_banner("Utils Module Tests")
    
    print(f"Timestamp: {get_timestamp()}")
    print(f"Tokens estimados en 'Hello World': {count_tokens('Hello World')}")
    print(f"Costo estimado (100 tokens in, 50 out): ${estimate_cost(100, 50):.4f}")
    
    print("\n✓ Utils module funcionando correctamente")
