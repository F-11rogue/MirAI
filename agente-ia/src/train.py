"""
Script de entrenamiento para el agente de IA
Permite entrenar diferentes tipos de agentes con datos personalizados
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

from agent import create_agent
from data_processor import load_training_data, prepare_data

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """Carga configuración desde archivo YAML"""
    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def train_conversational_agent(agent, training_data: List[Dict[str, Any]], config: Dict[str, Any]):
    """
    Entrena un agente conversacional.
    Para LLMs pre-entrenados, esto prepara los datos para fine-tuning.
    """
    logger.info("Entrenando agente conversacional...")
    
    # Preparar datos para fine-tuning si es necesario
    prepare_for_finetuning = config.get('training', {}).get('fine_tuning', False)
    
    agent.train(training_data, prepare_for_finetuning=prepare_for_finetuning)
    
    logger.info("Entrenamiento de agente conversacional completado!")
    return agent


def train_classifier_agent(agent, training_data: List[Dict[str, Any]], config: Dict[str, Any]):
    """Entrena un agente clasificador"""
    logger.info("Entrenando agente clasificador...")
    
    # El clasificador necesita datos con formato: {'text': ..., 'label': ...}
    agent.train(training_data)
    
    logger.info("Entrenamiento de agente clasificador completado!")
    return agent


def train_custom_agent(agent, training_data: List[Dict[str, Any]], config: Dict[str, Any]):
    """Entrena un agente personalizado"""
    logger.info("Entrenando agente personalizado...")
    
    agent.train(training_data)
    
    logger.info("Entrenamiento de agente personalizado completado!")
    return agent


def evaluate_agent(agent, test_data: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Evalúa el rendimiento del agente en datos de prueba.
    
    Args:
        agent: Agente entrenado
        test_data: Datos de prueba
    
    Returns:
        Dict con métricas de evaluación
    """
    logger.info(f"Evaluando agente con {len(test_data)} ejemplos de prueba...")
    
    correct = 0
    total = len(test_data)
    
    for item in test_data:
        input_text = item.get('text') or item.get('user')
        expected = item.get('label') or item.get('assistant')
        
        # Procesar con el agente
        response = agent.process(input_text)
        
        # Comparar (simplificado)
        if expected and expected.lower() in response.lower():
            correct += 1
    
    accuracy = correct / total if total > 0 else 0
    
    metrics = {
        'accuracy': accuracy,
        'total_samples': total,
        'correct_predictions': correct
    }
    
    logger.info(f"Métricas de evaluación: {metrics}")
    return metrics


def save_training_results(agent, metrics: Dict[str, float], output_path: str):
    """Guarda el agente entrenado y sus métricas"""
    # Crear directorio si no existe
    os.makedirs(output_path, exist_ok=True)
    
    # Guardar agente
    agent_path = os.path.join(output_path, 'agent.json')
    agent.save(agent_path)
    
    # Guardar métricas
    metrics_path = os.path.join(output_path, 'metrics.json')
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Resultados guardados en: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Entrena un agente de IA con tus datos personalizados'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/agent_config.yaml',
        help='Ruta al archivo de configuración del agente'
    )
    
    parser.add_argument(
        '--agent-type',
        type=str,
        choices=['conversational', 'classifier', 'custom'],
        help='Tipo de agente a entrenar (sobrescribe config)'
    )
    
    parser.add_argument(
        '--training-data',
        type=str,
        default='data/training/',
        help='Ruta a los datos de entrenamiento'
    )
    
    parser.add_argument(
        '--test-data',
        type=str,
        default=None,
        help='Ruta a los datos de prueba (opcional)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='models/trained/',
        help='Directorio donde guardar el modelo entrenado'
    )
    
    parser.add_argument(
        '--no-eval',
        action='store_true',
        help='No evaluar el agente después del entrenamiento'
    )
    
    args = parser.parse_args()
    
    try:
        # Cargar configuración
        logger.info(f"Cargando configuración desde: {args.config}")
        config = load_config(args.config)
        
        # Determinar tipo de agente
        agent_type = args.agent_type or config.get('agent', {}).get('type', 'conversational')
        logger.info(f"Tipo de agente: {agent_type}")
        
        # Crear agente
        logger.info("Creando agente...")
        agent = create_agent(agent_type, args.config)
        
        # Cargar datos de entrenamiento
        logger.info(f"Cargando datos de entrenamiento desde: {args.training_data}")
        training_data = load_training_data(args.training_data)
        
        if not training_data:
            logger.error("No se encontraron datos de entrenamiento!")
            logger.info("Coloca tus datos en el directorio especificado.")
            logger.info("Formatos soportados: .json, .jsonl, .csv")
            sys.exit(1)
        
        logger.info(f"Datos cargados: {len(training_data)} ejemplos")
        
        # Entrenar según tipo de agente
        if agent_type == 'conversational':
            agent = train_conversational_agent(agent, training_data, config)
        elif agent_type == 'classifier':
            agent = train_classifier_agent(agent, training_data, config)
        elif agent_type == 'custom':
            agent = train_custom_agent(agent, training_data, config)
        
        # Evaluar si hay datos de prueba
        metrics = {}
        if not args.no_eval and args.test_data:
            logger.info(f"Cargando datos de prueba desde: {args.test_data}")
            test_data = load_training_data(args.test_data)
            
            if test_data:
                metrics = evaluate_agent(agent, test_data)
        
        # Guardar resultados
        logger.info(f"Guardando modelo en: {args.output}")
        save_training_results(agent, metrics, args.output)
        
        logger.info("✓ Entrenamiento completado exitosamente!")
        logger.info(f"Para usar el agente, ejecuta: python src/inference.py --model {args.output}")
        
    except FileNotFoundError as e:
        logger.error(f"Archivo no encontrado: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error durante el entrenamiento: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
