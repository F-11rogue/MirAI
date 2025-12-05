"""
Paquete principal del Agente de IA
"""

__version__ = "1.0.0"
__author__ = "MirAI Project"

from .agent import (
    BaseAgent,
    ConversationalAgent,
    ClassifierAgent,
    CustomAgent,
    create_agent
)

__all__ = [
    'BaseAgent',
    'ConversationalAgent',
    'ClassifierAgent',
    'CustomAgent',
    'create_agent'
]
