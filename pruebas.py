import logging
import re
import pandas as pd
from datetime import datetime
from typing import Dict, Tuple, Optional

# Importa las clases y funciones necesarias
import negociador.negociador as negociador
from funciones.microphone import MicrophoneManager
from funciones.transcription import SpeechToText
from funciones.text_to_speech import text_to_speech_gtts

def main():
    # Inicializa los módulos
    mic_manager = MicrophoneManager(rate=16000, channels=1, chunk_duration=0.25)
    speech_to_text = SpeechToText(model_id="openai/whisper-tiny", device="cpu")
    negotiator = negociador.DebtNegotiator()
    conversation_state = {
        'client_verified': False,
        'negotiation_stage': 'identification',
        'messages': [],
        'client_data': None
    }
    
    print("Escribe 'iniciar llamada' para comenzar o 'finalizar llamada' para terminar.")
    
    # Esperar hasta que el usuario inicie la llamada
    while True:
        command = input("\nUsuario: ").strip().lower()
        
        if command == "iniciar llamada":
            print("Llamada iniciada. Saluda a la máquina.")
            initial_greeting = input("\nUsuario (saludo): ").strip()
            
            # La máquina responde al saludo
            response, _ = negotiator.get_response(initial_greeting, conversation_state)
            print(f"Asistente: {response}")
            text_to_speech_gtts(response, lang="es")
            break
        
        elif command == "finalizar llamada":
            print("No se inició la llamada. Fin del programa.")
            return
        else:
            print("Comando no reconocido. Usa 'iniciar llamada' o 'finalizar llamada'.")
    
    # Ciclo principal de la llamada
    try:
        mic_manager.start_microphone()
        
        while True:
            command = input("\nEscribe 'responder' para hablar o 'finalizar llamada' para terminar: ").strip().lower()
            
            if command == "responder":
                print("Grabando... habla ahora.")
                audio_array = mic_manager.record_audio(duration=5)
                user_input = speech_to_text.transcribe(audio_array).strip()
                
                print(f"Tú dijiste: {user_input}")
                
                # Procesa la entrada del usuario con el negociador
                response, should_end = negotiator.get_response(user_input, conversation_state)
                
                # Actualiza el historial de la conversación
                conversation_state['messages'].append({
                    'role': 'user',
                    'content': user_input,
                    'timestamp': datetime.now().isoformat()
                })
                conversation_state['messages'].append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().isoformat()
                })
                
                print(f"Asistente: {response}")
                
                # Genera audio con la respuesta
                text_to_speech_gtts(response, lang="es")
                
                if should_end:
                    print("\nLa negociación ha terminado.")
                    break
            
            elif command == "finalizar llamada":
                print("Llamada finalizada. Gracias por usar el sistema.")
                break
            
            else:
                print("Comando no reconocido. Usa 'responder' o 'finalizar llamada'.")
    
    finally:
        # Detiene el micrófono
        mic_manager.stop_microphone()

if __name__ == "__main__":
    main()
