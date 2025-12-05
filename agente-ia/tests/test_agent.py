"""
Tests unitarios para el agente de IA
"""

import pytest
import sys
import os

# Agregar directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent import BaseAgent, ConversationalAgent, ClassifierAgent, CustomAgent, create_agent


class TestAgentCreation:
    """Tests para la creación de agentes"""
    
    def test_create_conversational_agent(self):
        """Test crear agente conversacional"""
        agent = create_agent('conversational', '../config/agent_config.yaml')
        assert agent is not None
        assert isinstance(agent, ConversationalAgent)
        assert agent.name is not None
    
    def test_create_classifier_agent(self):
        """Test crear agente clasificador"""
        agent = create_agent('classifier', '../config/agent_config.yaml')
        assert agent is not None
        assert isinstance(agent, ClassifierAgent)
    
    def test_create_custom_agent(self):
        """Test crear agente personalizado"""
        agent = create_agent('custom', '../config/agent_config.yaml')
        assert agent is not None
        assert isinstance(agent, CustomAgent)
    
    def test_invalid_agent_type(self):
        """Test tipo de agente inválido"""
        with pytest.raises(ValueError):
            create_agent('invalid_type')


class TestCustomAgent:
    """Tests para agente personalizado"""
    
    def test_custom_agent_process(self):
        """Test procesamiento de agente personalizado"""
        agent = CustomAgent()
        response = agent.process("Test input")
        assert response is not None
        assert "Echo" in response
    
    def test_custom_agent_history(self):
        """Test historial de agente"""
        agent = CustomAgent()
        agent.process("Input 1")
        agent.process("Input 2")
        
        history = agent.get_history()
        assert len(history) == 2
        assert history[0]['user'] == "Input 1"
        assert history[1]['user'] == "Input 2"
    
    def test_custom_agent_save_load(self, tmp_path):
        """Test guardar y cargar agente"""
        agent = CustomAgent()
        agent.process("Test")
        
        # Guardar
        save_path = os.path.join(tmp_path, "agent.json")
        agent.save(save_path)
        assert os.path.exists(save_path)
        
        # Cargar
        loaded_agent = CustomAgent.load(save_path)
        assert loaded_agent.name == agent.name


class TestClassifierAgent:
    """Tests para agente clasificador"""
    
    def test_classifier_training(self):
        """Test entrenamiento de clasificador"""
        agent = ClassifierAgent()
        
        training_data = [
            {'text': 'Quiero agendar una cita', 'label': 'agendar'},
            {'text': '¿Cuánto cuesta?', 'label': 'precio'},
            {'text': '¿Dónde están?', 'label': 'ubicacion'},
            {'text': 'Necesito cambiar mi cita', 'label': 'agendar'},
            {'text': '¿Cuál es el precio?', 'label': 'precio'},
        ]
        
        report = agent.train(training_data)
        assert report is not None
        assert agent.model is not None
        assert agent.vectorizer is not None
    
    def test_classifier_prediction(self):
        """Test predicción de clasificador"""
        agent = ClassifierAgent()
        
        training_data = [
            {'text': 'Quiero agendar', 'label': 'agendar'},
            {'text': '¿Precio?', 'label': 'precio'},
            {'text': 'Ubicación', 'label': 'ubicacion'},
            {'text': 'Agendar cita', 'label': 'agendar'},
            {'text': 'Costo', 'label': 'precio'},
        ]
        
        agent.train(training_data)
        
        # Predecir
        result = agent.process("Quiero hacer una cita")
        assert result is not None
        assert "Categoría" in result


class TestDataProcessing:
    """Tests para procesamiento de datos"""
    
    def test_load_json_data(self, tmp_path):
        """Test cargar datos JSON"""
        from data_processor import load_json_file, save_processed_data
        
        # Crear datos de prueba
        test_data = [
            {'user': 'Hola', 'assistant': 'Hola, ¿cómo puedo ayudarte?'}
        ]
        
        json_path = os.path.join(tmp_path, "test.json")
        save_processed_data(test_data, json_path)
        
        # Cargar
        loaded_data = load_json_file(json_path)
        assert len(loaded_data) == 1
        assert loaded_data[0]['user'] == 'Hola'
    
    def test_split_data(self):
        """Test división de datos"""
        from data_processor import split_data
        
        data = [{'id': i} for i in range(100)]
        train, val, test = split_data(data, 0.7, 0.15, 0.15)
        
        assert len(train) == 70
        assert len(val) == 15
        assert len(test) == 15


class TestUtils:
    """Tests para utilidades"""
    
    def test_count_tokens(self):
        """Test conteo de tokens"""
        from utils import count_tokens
        
        text = "Hola mundo"
        tokens = count_tokens(text)
        assert tokens > 0
    
    def test_truncate_text(self):
        """Test truncar texto"""
        from utils import truncate_text
        
        long_text = "a" * 200
        truncated = truncate_text(long_text, max_length=50)
        assert len(truncated) <= 50
        assert truncated.endswith("...")
    
    def test_estimate_cost(self):
        """Test estimación de costo"""
        from utils import estimate_cost
        
        cost = estimate_cost(1000, 500, "gpt-3.5-turbo")
        assert cost > 0
        assert cost < 0.01  # Debería ser muy bajo para estas cantidades


# Funciones de fixture
@pytest.fixture
def sample_agent():
    """Fixture para crear un agente de ejemplo"""
    return CustomAgent()


@pytest.fixture
def sample_training_data():
    """Fixture para datos de entrenamiento de ejemplo"""
    return [
        {'text': 'Hola', 'label': 'saludo'},
        {'text': 'Adiós', 'label': 'despedida'},
        {'text': 'Gracias', 'label': 'agradecimiento'},
    ]


if __name__ == "__main__":
    # Ejecutar tests con pytest
    pytest.main([__file__, '-v'])
