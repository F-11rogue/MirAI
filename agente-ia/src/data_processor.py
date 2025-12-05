"""
Procesador de datos para el agente de IA
Maneja la carga, limpieza y preparación de datos
"""

import os
import json
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def load_json_file(file_path: str) -> List[Dict[str, Any]]:
    """Carga datos desde un archivo JSON"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return [data]
    else:
        logger.warning(f"Formato JSON inesperado en {file_path}")
        return []


def load_jsonl_file(file_path: str) -> List[Dict[str, Any]]:
    """Carga datos desde un archivo JSONL (JSON Lines)"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def load_csv_file(file_path: str) -> List[Dict[str, Any]]:
    """Carga datos desde un archivo CSV"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(dict(row))
    return data


def load_training_data(data_path: str) -> List[Dict[str, Any]]:
    """
    Carga datos de entrenamiento desde un archivo o directorio.
    Soporta formatos: JSON, JSONL, CSV
    
    Args:
        data_path: Ruta a archivo o directorio con datos
    
    Returns:
        Lista de ejemplos de entrenamiento
    """
    all_data = []
    
    # Si es un archivo
    if os.path.isfile(data_path):
        logger.info(f"Cargando archivo: {data_path}")
        
        if data_path.endswith('.json'):
            all_data.extend(load_json_file(data_path))
        elif data_path.endswith('.jsonl'):
            all_data.extend(load_jsonl_file(data_path))
        elif data_path.endswith('.csv'):
            all_data.extend(load_csv_file(data_path))
        else:
            logger.warning(f"Formato no soportado: {data_path}")
    
    # Si es un directorio
    elif os.path.isdir(data_path):
        logger.info(f"Cargando archivos desde directorio: {data_path}")
        
        for file_name in os.listdir(data_path):
            file_path = os.path.join(data_path, file_name)
            
            if not os.path.isfile(file_path):
                continue
            
            try:
                if file_name.endswith('.json'):
                    all_data.extend(load_json_file(file_path))
                elif file_name.endswith('.jsonl'):
                    all_data.extend(load_jsonl_file(file_path))
                elif file_name.endswith('.csv'):
                    all_data.extend(load_csv_file(file_path))
            except Exception as e:
                logger.error(f"Error cargando {file_path}: {e}")
    
    else:
        logger.error(f"Ruta no válida: {data_path}")
    
    logger.info(f"Total de ejemplos cargados: {len(all_data)}")
    return all_data


def prepare_data(
    data: List[Dict[str, Any]],
    format_type: str = 'conversational'
) -> List[Dict[str, Any]]:
    """
    Prepara y normaliza los datos al formato esperado.
    
    Args:
        data: Datos sin procesar
        format_type: Tipo de formato ('conversational' o 'classifier')
    
    Returns:
        Datos procesados
    """
    processed_data = []
    
    for item in data:
        if format_type == 'conversational':
            # Formato para agentes conversacionales
            # Espera: {'user': ..., 'assistant': ..., 'context': ...}
            processed_item = {
                'user': item.get('user') or item.get('input') or item.get('question') or '',
                'assistant': item.get('assistant') or item.get('output') or item.get('answer') or '',
                'context': item.get('context') or ''
            }
        
        elif format_type == 'classifier':
            # Formato para clasificadores
            # Espera: {'text': ..., 'label': ...}
            processed_item = {
                'text': item.get('text') or item.get('input') or item.get('user') or '',
                'label': item.get('label') or item.get('category') or item.get('class') or ''
            }
        
        else:
            processed_item = item
        
        # Solo agregar si tiene contenido válido
        if any(v for v in processed_item.values() if v):
            processed_data.append(processed_item)
    
    logger.info(f"Datos procesados: {len(processed_data)} ejemplos")
    return processed_data


def clean_text(text: str) -> str:
    """
    Limpia y normaliza texto.
    
    Args:
        text: Texto sin procesar
    
    Returns:
        Texto limpio
    """
    if not text:
        return ""
    
    # Remover espacios múltiples
    text = ' '.join(text.split())
    
    # Remover caracteres de control
    text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
    
    return text.strip()


def split_data(
    data: List[Dict[str, Any]],
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_seed: int = 42
) -> tuple:
    """
    Divide los datos en conjuntos de entrenamiento, validación y prueba.
    
    Args:
        data: Datos completos
        train_ratio: Proporción para entrenamiento
        val_ratio: Proporción para validación
        test_ratio: Proporción para prueba
        random_seed: Semilla para reproducibilidad
    
    Returns:
        Tuple de (train_data, val_data, test_data)
    """
    import random
    
    # Verificar proporciones
    total = train_ratio + val_ratio + test_ratio
    if abs(total - 1.0) > 0.01:
        raise ValueError(f"Las proporciones deben sumar 1.0, suman {total}")
    
    # Mezclar datos
    random.seed(random_seed)
    shuffled_data = data.copy()
    random.shuffle(shuffled_data)
    
    # Calcular índices
    n = len(shuffled_data)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)
    
    # Dividir
    train_data = shuffled_data[:train_end]
    val_data = shuffled_data[train_end:val_end]
    test_data = shuffled_data[val_end:]
    
    logger.info(f"Datos divididos: Train={len(train_data)}, Val={len(val_data)}, Test={len(test_data)}")
    
    return train_data, val_data, test_data


def save_processed_data(data: List[Dict[str, Any]], output_path: str):
    """
    Guarda datos procesados en formato JSON.
    
    Args:
        data: Datos a guardar
        output_path: Ruta del archivo de salida
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Datos guardados en: {output_path}")


def create_example_data(output_dir: str = "data/training/"):
    """
    Crea datos de ejemplo para empezar rápidamente.
    
    Args:
        output_dir: Directorio donde guardar los ejemplos
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Datos de ejemplo para agente conversacional
    conversational_data = [
        {
            "user": "¿Cuál es el horario de atención?",
            "assistant": "Nuestro horario de atención es de lunes a sábado, de 9:00 AM a 6:00 PM.",
            "context": "info_general"
        },
        {
            "user": "¿Cómo puedo agendar una cita?",
            "assistant": "Puedes agendar una cita a través de nuestro WhatsApp al +57 310 342 3456, por nuestro formulario web, o llamando directamente.",
            "context": "agendar"
        },
        {
            "user": "¿Cuánto cuesta el servicio de manicure?",
            "assistant": "El servicio de manicure tiene un precio desde $50.000. El costo exacto puede variar según el diseño y técnica.",
            "context": "precios"
        },
        {
            "user": "¿Dónde están ubicados?",
            "assistant": "Estamos ubicados en Bogotá, Colombia. Puedes encontrar la dirección exacta en nuestra página de contacto.",
            "context": "ubicacion"
        },
        {
            "user": "¿Qué servicios ofrecen?",
            "assistant": "Ofrecemos servicios de manicure, pedicure, diseño de uñas, acrílico escultórico, y cuidado de la piel.",
            "context": "servicios"
        }
    ]
    
    # Datos de ejemplo para clasificador
    classifier_data = [
        {"text": "¿Cuál es el horario?", "label": "consulta_horario"},
        {"text": "Quiero agendar una cita", "label": "solicitud_cita"},
        {"text": "¿Cuánto cuesta?", "label": "consulta_precio"},
        {"text": "¿Dónde están?", "label": "consulta_ubicacion"},
        {"text": "¿Qué servicios tienen?", "label": "consulta_servicios"},
        {"text": "Necesito cambiar mi cita", "label": "modificar_cita"},
        {"text": "¿Aceptan tarjeta?", "label": "consulta_pago"},
        {"text": "¿Tienen estacionamiento?", "label": "consulta_instalaciones"}
    ]
    
    # Guardar datos
    save_processed_data(
        conversational_data,
        os.path.join(output_dir, "example_conversational.json")
    )
    
    save_processed_data(
        classifier_data,
        os.path.join(output_dir, "example_classifier.json")
    )
    
    logger.info(f"Datos de ejemplo creados en: {output_dir}")
    logger.info("- example_conversational.json: Para agentes conversacionales")
    logger.info("- example_classifier.json: Para agentes clasificadores")


if __name__ == "__main__":
    # Crear datos de ejemplo
    create_example_data()
