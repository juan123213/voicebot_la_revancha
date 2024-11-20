import logging
from datetime import datetime
from typing import Dict
from funciones.microphone import MicrophoneManager
from funciones.transcription import SpeechToText
from funciones.text_to_speech_gtts import text_to_speech_gtts
from negociador.negociador import DebtNegotiator

def print_separator():
    print("\n" + "="*50 + "\n")

def print_sentiment_analysis(analysis):
    print("\nAnálisis de Sentimientos:")
    print(f"Sentimiento: {analysis['sentiment']}")
    print(f"Puntuación: {analysis['score']:.2f}")
    if 'context_type' in analysis:
        print(f"Tipo de contexto: {analysis['context_type']}")
    if 'keywords_detected' in analysis:
        print("Palabras clave detectadas:")
        for category, words in analysis['keywords_detected'].items():
            print(f"  - {category}: {', '.join(words)}")
    print("-"*30)

def print_metrics(metrics: Dict):
    print("\n=== MÉTRICAS DE LA CONVERSACIÓN ===")
    print(f"Total interacciones: {metrics['total_interactions']}")
    
    print("\nDistribución de sentimientos:")
    for sentiment, count in metrics['sentiment_distribution'].items():
        print(f"- {sentiment}: {count}")
    
    print(f"\nTendencia: {metrics['sentiment_trend']}")
    print(f"Puntuación promedio: {metrics['average_sentiment_score']:.2f}")
    
    print("\nFrecuencia de palabras clave:")
    for category, count in metrics['keywords_frequency'].items():
        if count > 0:  # Solo mostrar categorías con ocurrencias
            print(f"- {category}: {count}")
    
    print(f"\nProbabilidad de éxito: {metrics['negotiation_success_probability']*100:.1f}%")

def main():
    print("Iniciando sistema de negociación...")
    mic_manager = MicrophoneManager(rate=16000, channels=1, chunk_duration=0.25)
    speech_to_text = SpeechToText(model_id="openai/whisper-tiny", device="cpu")
    negotiator = DebtNegotiator()
    
    conversation_state = {
        'client_verified': False,
        'negotiation_stage': 'identification',
        'messages': [],
        'client_data': None,
        'sentiment_history': [],
        'offer_attempts': 0,
        'conversation_flow': [],
        'context': {},
        'last_message_type': None
    }
    
    print("\nEscribe 'iniciar llamada' para comenzar o 'finalizar llamada' para terminar.")
    
    try:
        while True:
            command = input("\nUsuario: ").strip().lower()
            
            if command == "iniciar llamada":
                print("Llamada iniciada. Saluda a la máquina.")
                initial_greeting = input("\nUsuario (saludo): ").strip()
                
                response, end_conversation, metrics = negotiator.get_response(initial_greeting, conversation_state)
                print(f"\nAsistente: {response}\n")
                
                if conversation_state.get('sentiment_history'):
                    print_sentiment_analysis(conversation_state['sentiment_history'][-1])
                
                text_to_speech_gtts(response, lang="es")
                break
                
            elif command == "finalizar llamada":
                print("No se inició la llamada. Fin del programa.")
                return
            else:
                print("Comando no reconocido. Usa 'iniciar llamada' o 'finalizar llamada'.")
        
        mic_manager.start_microphone()
        
        while True:
            command = input("\nEscribe 'responder' para hablar, 'metricas' para ver análisis o 'finalizar' para terminar: ").strip().lower()
            
            if command == "responder":
                print("Grabando... habla ahora.")
                audio_array = mic_manager.record_audio(duration=5)
                
                print("Transcribiendo audio...")
                user_input = speech_to_text.transcribe(audio_array).strip()
                
                if not user_input or len(user_input) < 2:
                    print("No se detectó audio claro. Por favor, intenta de nuevo.")
                    continue
                
                print(f"\nTú dijiste: {user_input}")
                
                response, end_conversation, metrics = negotiator.get_response(user_input, conversation_state)
                print(f"\nAsistente: {response}\n")
                
                if conversation_state.get('sentiment_history'):
                    print_sentiment_analysis(conversation_state['sentiment_history'][-1])
                
                text_to_speech_gtts(response, lang="es")
                
                if end_conversation:
                    print("\n=== REPORTE FINAL DE LA CONVERSACIÓN ===")
                    final_metrics = negotiator.sentiment_analyzer.get_conversation_metrics()
                    print_metrics(final_metrics)
                    break
            
            elif command == "metricas":
                metrics = negotiator.sentiment_analyzer.get_conversation_metrics()
                print_metrics(metrics)
            
            elif command == "finalizar":
                print("\n=== REPORTE FINAL DE LA CONVERSACIÓN ===")
                final_metrics = negotiator.sentiment_analyzer.get_conversation_metrics()
                print_metrics(final_metrics)
                print("\nLlamada finalizada. Gracias por usar el sistema.")
                break
            
            else:
                print("Comando no reconocido. Usa 'responder', 'metricas' o 'finalizar'")
    
    except Exception as e:
        print(f"\nError en la ejecución: {str(e)}")
    
    finally:
        mic_manager.stop_microphone()
        print("\nSistema finalizado.")

if __name__ == "__main__":
    main()