"""
Script de inferencia para usar el agente entrenado
Permite interactuar con el agente de diferentes formas
"""

import os
import sys
import argparse
import logging
from typing import Optional

from agent import create_agent

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def interactive_mode(agent):
    """
    Modo interactivo: conversa con el agente en tiempo real.
    """
    print("\n" + "="*60)
    print(f"🤖 Agente: {agent.name} v{agent.version}")
    print("="*60)
    print("Modo Interactivo")
    print("Escribe 'salir' o 'exit' para terminar")
    print("Escribe 'historial' para ver el historial de conversación")
    print("Escribe 'limpiar' para limpiar el historial")
    print("="*60 + "\n")
    
    while True:
        try:
            # Leer entrada del usuario
            user_input = input("Tú: ").strip()
            
            if not user_input:
                continue
            
            # Comandos especiales
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print("\n👋 ¡Hasta luego!")
                break
            
            elif user_input.lower() == 'historial':
                history = agent.get_history()
                if not history:
                    print("📝 No hay historial aún.\n")
                else:
                    print("\n📝 Historial de conversación:")
                    for i, interaction in enumerate(history, 1):
                        print(f"\n[{i}] {interaction['timestamp']}")
                        print(f"  Tú: {interaction['user']}")
                        print(f"  Agente: {interaction['agent']}")
                    print()
                continue
            
            elif user_input.lower() == 'limpiar':
                agent.history = []
                print("🧹 Historial limpiado.\n")
                continue
            
            # Procesar con el agente
            response = agent.process(user_input)
            print(f"Agente: {response}\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"❌ Error: {e}\n")


def batch_mode(agent, input_file: str, output_file: Optional[str] = None):
    """
    Modo batch: procesa un archivo de entradas.
    """
    logger.info(f"Procesando archivo: {input_file}")
    
    try:
        # Leer archivo de entrada
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        results = []
        
        print(f"\nProcesando {len(lines)} líneas...\n")
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            print(f"[{i}] Procesando: {line}")
            response = agent.process(line)
            print(f"    Respuesta: {response}\n")
            
            results.append({
                'input': line,
                'output': response
            })
        
        # Guardar resultados si se especifica archivo de salida
        if output_file:
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Resultados guardados en: {output_file}")
        
        logger.info("✓ Procesamiento completado!")
    
    except FileNotFoundError:
        logger.error(f"Archivo no encontrado: {input_file}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error procesando archivo: {e}")
        sys.exit(1)


def single_query_mode(agent, query: str):
    """
    Modo de consulta única: procesa una sola pregunta.
    """
    print(f"\nPregunta: {query}")
    response = agent.process(query)
    print(f"Respuesta: {response}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Usa el agente de IA entrenado para generar respuestas'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/agent_config.yaml',
        help='Ruta al archivo de configuración del agente'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default=None,
        help='Ruta al modelo entrenado guardado (opcional)'
    )
    
    parser.add_argument(
        '--agent-type',
        type=str,
        choices=['conversational', 'classifier', 'custom'],
        default='conversational',
        help='Tipo de agente a usar'
    )
    
    # Modos de operación
    mode_group = parser.add_mutually_exclusive_group()
    
    mode_group.add_argument(
        '--interactive',
        action='store_true',
        help='Modo interactivo (conversación en tiempo real)'
    )
    
    mode_group.add_argument(
        '--input',
        type=str,
        help='Archivo de entrada para procesamiento batch'
    )
    
    mode_group.add_argument(
        '--query',
        type=str,
        help='Consulta única'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Archivo de salida para resultados batch (opcional)'
    )
    
    args = parser.parse_args()
    
    try:
        # Cargar o crear agente
        if args.model:
            logger.info(f"Cargando modelo desde: {args.model}")
            # Crear agente según tipo y cargar su configuración
            agent = create_agent(args.agent_type, args.config)
            
            # Cargar el estado guardado si existe
            model_path = os.path.join(args.model, 'agent.json')
            if os.path.exists(model_path):
                with open(model_path, 'r', encoding='utf-8') as f:
                    import json
                    save_data = json.load(f)
                    agent.config = save_data.get('config', agent.config)
                    agent.name = save_data.get('name', agent.name)
                logger.info(f"Estado del modelo cargado desde: {model_path}")
        else:
            logger.info(f"Creando nuevo agente tipo: {args.agent_type}")
            agent = create_agent(args.agent_type, args.config)
        
        # Ejecutar según modo
        if args.interactive:
            interactive_mode(agent)
        
        elif args.input:
            batch_mode(agent, args.input, args.output)
        
        elif args.query:
            single_query_mode(agent, args.query)
        
        else:
            # Por defecto, modo interactivo
            interactive_mode(agent)
    
    except FileNotFoundError as e:
        logger.error(f"Archivo no encontrado: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
