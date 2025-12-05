"""
Módulo principal del Agente de IA
Contiene las clases base y diferentes tipos de agentes
"""

import os
import json
import yaml
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Clase base abstracta para todos los agentes.
    Define la interfaz común que todos los agentes deben implementar.
    """
    
    def __init__(self, config_path: str = "config/agent_config.yaml"):
        """
        Inicializa el agente con su configuración.
        
        Args:
            config_path: Ruta al archivo de configuración YAML
        """
        self.config = self._load_config(config_path)
        self.name = self.config.get('agent', {}).get('name', 'Agent')
        self.version = self.config.get('agent', {}).get('version', '1.0.0')
        self.history = []
        
        logger.info(f"Inicializando {self.name} v{self.version}")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Carga la configuración desde archivo YAML"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Configuración no encontrada: {config_path}, usando defaults")
            return {}
    
    @abstractmethod
    def process(self, input_text: str, **kwargs) -> str:
        """
        Procesa una entrada y genera una respuesta.
        Debe ser implementado por cada tipo de agente.
        
        Args:
            input_text: Texto de entrada del usuario
            **kwargs: Argumentos adicionales específicos del agente
            
        Returns:
            str: Respuesta generada por el agente
        """
        pass
    
    @abstractmethod
    def train(self, training_data: List[Dict[str, Any]], **kwargs):
        """
        Entrena el agente con datos de entrenamiento.
        
        Args:
            training_data: Lista de ejemplos de entrenamiento
            **kwargs: Parámetros de entrenamiento adicionales
        """
        pass
    
    def save(self, path: str):
        """Guarda el estado del agente"""
        save_data = {
            'name': self.name,
            'version': self.version,
            'config': self.config,
            'timestamp': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Agente guardado en: {path}")
    
    @classmethod
    def load(cls, path: str, config_path: str = "config/agent_config.yaml"):
        """
        Carga un agente guardado.
        
        Args:
            path: Ruta al archivo JSON del agente guardado
            config_path: Ruta opcional al archivo de configuración
        
        Returns:
            Instancia del agente cargado
        """
        with open(path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        # Obtener configuración del archivo guardado
        saved_config = save_data.get('config', {})
        
        # Crear instancia con la configuración guardada
        # Primero intentamos crear el agente con config_path
        agent = cls(config_path)
        
        # Luego sobrescribimos con la configuración guardada si existe
        if saved_config:
            agent.config = saved_config
        
        # Restaurar otros atributos
        agent.name = save_data.get('name', agent.name)
        agent.version = save_data.get('version', agent.version)
        
        logger.info(f"Agente cargado desde: {path}")
        return agent
    
    def add_to_history(self, user_input: str, agent_response: str):
        """Agrega una interacción al historial"""
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_input,
            'agent': agent_response
        })
    
    def get_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """Obtiene el historial de conversación"""
        if limit:
            return self.history[-limit:]
        return self.history


class ConversationalAgent(BaseAgent):
    """
    Agente conversacional que usa LLMs (OpenAI, Anthropic, etc.)
    para mantener conversaciones naturales.
    """
    
    def __init__(self, config_path: str = "config/agent_config.yaml"):
        super().__init__(config_path)
        self.model_config = self.config.get('model', {})
        self.provider = self.model_config.get('provider', 'openai')
        self.model_name = self.model_config.get('model_name', 'gpt-3.5-turbo')
        
        # Inicializar cliente según proveedor
        self._init_client()
    
    def _init_client(self):
        """Inicializa el cliente del LLM según el proveedor"""
        try:
            if self.provider == 'openai':
                from openai import OpenAI
                self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                logger.info(f"Cliente OpenAI inicializado con modelo: {self.model_name}")
            
            elif self.provider == 'anthropic':
                from anthropic import Anthropic
                self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                logger.info(f"Cliente Anthropic inicializado con modelo: {self.model_name}")
            
            else:
                logger.warning(f"Proveedor {self.provider} no soportado directamente")
                self.client = None
        
        except ImportError as e:
            logger.error(f"Error importando librería: {e}")
            logger.info("Instala las dependencias con: pip install openai anthropic")
            self.client = None
    
    def process(self, input_text: str, context: Optional[str] = None, **kwargs) -> str:
        """
        Procesa una entrada y genera una respuesta usando el LLM.
        
        Args:
            input_text: Texto de entrada del usuario
            context: Contexto adicional para la conversación
            **kwargs: Parámetros adicionales (temperature, max_tokens, etc.)
        
        Returns:
            str: Respuesta generada por el LLM
        """
        if not self.client:
            return "Lo siento, el agente no está configurado correctamente. Revisa tu API key."
        
        # Construir mensajes
        messages = self._build_messages(input_text, context)
        
        # Obtener parámetros
        params = self._get_generation_params(**kwargs)
        
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    **params
                )
                answer = response.choices[0].message.content
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model_name,
                    messages=messages,
                    **params
                )
                answer = response.content[0].text
            
            else:
                answer = "Proveedor no soportado"
            
            # Guardar en historial
            self.add_to_history(input_text, answer)
            
            return answer
        
        except Exception as e:
            logger.error(f"Error al generar respuesta: {e}")
            return f"Lo siento, ocurrió un error: {str(e)}"
    
    def _build_messages(self, input_text: str, context: Optional[str] = None) -> List[Dict[str, str]]:
        """Construye la lista de mensajes para el LLM"""
        messages = []
        
        # System prompt
        system_prompt = self.config.get('prompts', {}).get('system_prompt', '')
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Few-shot examples
        examples = self.config.get('prompts', {}).get('few_shot_examples', [])
        for example in examples:
            messages.append({"role": "user", "content": example['user']})
            messages.append({"role": "assistant", "content": example['assistant']})
        
        # Historial reciente
        memory_config = self.config.get('memory', {})
        max_messages = memory_config.get('max_messages', 5)
        recent_history = self.get_history(limit=max_messages)
        
        for interaction in recent_history:
            messages.append({"role": "user", "content": interaction['user']})
            messages.append({"role": "assistant", "content": interaction['agent']})
        
        # Contexto adicional
        if context:
            messages.append({"role": "system", "content": f"Contexto: {context}"})
        
        # Mensaje actual del usuario
        messages.append({"role": "user", "content": input_text})
        
        return messages
    
    def _get_generation_params(self, **kwargs) -> Dict[str, Any]:
        """Obtiene parámetros de generación desde config o kwargs"""
        agent_params = self.config.get('agent', {}).get('parameters', {})
        
        return {
            'temperature': kwargs.get('temperature', agent_params.get('temperature', 0.7)),
            'max_tokens': kwargs.get('max_tokens', agent_params.get('max_tokens', 500)),
            'top_p': kwargs.get('top_p', agent_params.get('top_p', 0.9)),
        }
    
    def train(self, training_data: List[Dict[str, Any]], **kwargs):
        """
        Los LLMs pre-entrenados no requieren entrenamiento adicional.
        Este método puede usarse para fine-tuning si es necesario.
        """
        logger.info("Los modelos LLM pre-entrenados no requieren entrenamiento.")
        logger.info("Para fine-tuning, considera usar la API de OpenAI o Hugging Face.")
        
        # Aquí podrías implementar fine-tuning si es necesario
        # Por ejemplo, preparar datos para OpenAI fine-tuning
        if kwargs.get('prepare_for_finetuning', False):
            self._prepare_finetuning_data(training_data)
    
    def _prepare_finetuning_data(self, training_data: List[Dict[str, Any]]):
        """Prepara datos en formato para fine-tuning"""
        output_file = "data/training/finetuning_data.jsonl"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in training_data:
                formatted = {
                    "messages": [
                        {"role": "user", "content": item.get('user', '')},
                        {"role": "assistant", "content": item.get('assistant', '')}
                    ]
                }
                f.write(json.dumps(formatted, ensure_ascii=False) + '\n')
        
        logger.info(f"Datos preparados para fine-tuning: {output_file}")


class ClassifierAgent(BaseAgent):
    """
    Agente clasificador que usa machine learning tradicional
    para clasificar textos en categorías.
    """
    
    def __init__(self, config_path: str = "config/agent_config.yaml"):
        super().__init__(config_path)
        self.model = None
        self.vectorizer = None
        self.classes = None
    
    def process(self, input_text: str, **kwargs) -> str:
        """
        Clasifica el texto de entrada.
        
        Args:
            input_text: Texto a clasificar
        
        Returns:
            str: Categoría predicha
        """
        if not self.model or not self.vectorizer:
            return "El modelo no está entrenado. Ejecuta train() primero."
        
        # Vectorizar entrada
        X = self.vectorizer.transform([input_text])
        
        # Predecir
        prediction = self.model.predict(X)[0]
        confidence = max(self.model.predict_proba(X)[0])
        
        result = f"Categoría: {prediction} (confianza: {confidence:.2%})"
        self.add_to_history(input_text, result)
        
        return result
    
    def train(self, training_data: List[Dict[str, Any]], **kwargs):
        """
        Entrena el clasificador con datos etiquetados.
        
        Args:
            training_data: Lista de dicts con 'text' y 'label'
            
        Ejemplo:
            [
                {'text': '¿Cuál es el precio?', 'label': 'consulta_precio'},
                {'text': 'Quiero agendar', 'label': 'solicitud_cita'},
            ]
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import classification_report
        
        logger.info(f"Entrenando clasificador con {len(training_data)} ejemplos")
        
        # Preparar datos
        texts = [item['text'] for item in training_data]
        labels = [item['label'] for item in training_data]
        self.classes = list(set(labels))
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42
        )
        
        # Vectorizar
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Entrenar
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train_vec, y_train)
        
        # Evaluar
        y_pred = self.model.predict(X_test_vec)
        report = classification_report(y_test, y_pred)
        
        logger.info(f"Entrenamiento completado!\n{report}")
        
        return report


class CustomAgent(BaseAgent):
    """
    Plantilla para crear tu propio agente personalizado.
    Hereda de BaseAgent e implementa la lógica específica que necesites.
    """
    
    def __init__(self, config_path: str = "config/agent_config.yaml"):
        super().__init__(config_path)
        # Inicializa aquí tus componentes personalizados
        logger.info("CustomAgent inicializado")
    
    def process(self, input_text: str, **kwargs) -> str:
        """
        Implementa aquí la lógica de procesamiento de tu agente.
        """
        # Ejemplo simple: eco con timestamp
        response = f"[{datetime.now().strftime('%H:%M:%S')}] Echo: {input_text}"
        self.add_to_history(input_text, response)
        return response
    
    def train(self, training_data: List[Dict[str, Any]], **kwargs):
        """
        Implementa aquí la lógica de entrenamiento de tu agente.
        """
        logger.info("Entrenando CustomAgent...")
        # Tu lógica de entrenamiento aquí
        logger.info("Entrenamiento completado!")


# Factory para crear agentes
def create_agent(agent_type: str, config_path: str = "config/agent_config.yaml") -> BaseAgent:
    """
    Factory function para crear diferentes tipos de agentes.
    
    Args:
        agent_type: Tipo de agente ('conversational', 'classifier', 'custom')
        config_path: Ruta al archivo de configuración
    
    Returns:
        BaseAgent: Instancia del agente solicitado
    """
    agents = {
        'conversational': ConversationalAgent,
        'classifier': ClassifierAgent,
        'custom': CustomAgent
    }
    
    agent_class = agents.get(agent_type.lower())
    if not agent_class:
        raise ValueError(f"Tipo de agente '{agent_type}' no soportado. "
                        f"Opciones: {list(agents.keys())}")
    
    return agent_class(config_path)


if __name__ == "__main__":
    # Ejemplo de uso
    print("=== Ejemplo de Uso de Agentes ===\n")
    
    # Crear un agente conversacional
    agent = create_agent('conversational')
    
    # Procesar una consulta
    response = agent.process("¿Cuál es el horario de atención?")
    print(f"Respuesta: {response}")
