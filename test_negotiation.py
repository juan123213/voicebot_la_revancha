from negociador.negociador import DebtNegotiator
import time
import json
from typing import Dict

def print_separator():
    print("\n" + "="*50 + "\n")

def print_sentiment_analysis(analysis):
    print("\nAnálisis de Sentimientos:")
    print(f"Sentimiento: {analysis['sentiment']}")
    print(f"Puntuación: {analysis['score']:.2f}")
    print(f"Timestamp: {analysis['timestamp']}")
    print("-"*30)

def print_metrics(metrics: Dict):
    print("\n=== MÉTRICAS FINALES DE LA CONVERSACIÓN ===")
    
    print("\nDistribución de sentimientos:")
    for sentiment, count in metrics['sentiment_distribution'].items():
        print(f"- {sentiment}: {count}")
    
    print(f"\nTendencia general: {metrics['sentiment_trend']}")
    print(f"Puntuación promedio: {metrics['average_sentiment_score']:.2f}")
    
    print("\nFrecuencia de palabras clave:")
    for category, count in metrics['keywords_frequency'].items():
        print(f"- {category}: {count}")
    
    print(f"\nProbabilidad de éxito en la negociación: {metrics['negotiation_success_probability']*100:.1f}%")
    
    print("\nLínea de tiempo:")
    for entry in metrics['timeline']:
        print(f"- {entry['timestamp'].split('T')[1][:8]} | "
              f"{entry['sentiment']} ({entry['score']:.2f}) | "
              f"Mensaje: '{entry['text']}'")

def test_negotiation():
    print("Iniciando prueba del sistema de negociación...")
    negotiator = DebtNegotiator()
    
    # Inicializar el estado de la conversación correctamente
    conversation_state = {
        "messages": [],
        "client_verified": False,
        "client_data": None,
        "negotiation_stage": "initial",
        "offer_attempts": 0,
        "last_message_type": None,
        "conversation_flow": [],
        "context": {},
        "sentiment_history": []
    }
    
    test_messages = [
        "Hola, necesito ayuda con una deuda",
        "Mi nombre es Miguel y mi DNI es 1234",
        "Me parece muy alto el monto",
        "¿Qué otras opciones tienen?",
        "Sí, acepto el plan de pago único"
    ]
    
    print_separator()
    print("Comenzando simulación de conversación...")
    print_separator()
    
    for i, message in enumerate(test_messages, 1):
        print(f"\nMensaje {i}/{len(test_messages)}: '{message}'")
        
        # Obtener respuesta y análisis
        response, end_conversation, metrics = negotiator.get_response(message, conversation_state)
        
        print(f"\nBot: {response}")
        
        # Mostrar análisis de sentimientos actual
        if conversation_state['sentiment_history']:
            current_sentiment = conversation_state['sentiment_history'][-1]
            print_sentiment_analysis(current_sentiment)
        
        # Mostrar métricas de la conversación actual
        print("\nMétricas de la conversación:")
        print(f"Total mensajes: {len(conversation_state['messages'])}")
        print(f"Etapa: {conversation_state['negotiation_stage']}")
        print(f"Cliente verificado: {'Sí' if conversation_state['client_verified'] else 'No'}")
        print(f"Intentos de oferta: {conversation_state['offer_attempts']}")
        
        if end_conversation:
            final_metrics = negotiator.sentiment_analyzer.get_conversation_metrics()
            print_metrics(final_metrics)
            break
        
        time.sleep(1)  # Pausa para mejor legibilidad
        print_separator()

if __name__ == "__main__":
    test_negotiation()