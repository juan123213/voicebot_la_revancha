from funciones.microphone import MicrophoneManager
from funciones.transcription import SpeechToText
from funciones.text_to_speech import text_to_speech_gtts

def main():
    # Inicializa los módulos
    mic_manager = MicrophoneManager(rate=16000, channels=1, chunk_duration=0.25)
    speech_to_text = SpeechToText(model_id="openai/whisper-tiny", device="cpu")

    try:
        # Inicia el micrófono
        mic_manager.start_microphone()

        # Graba y transcribe
        while True:
            command = input("Escribe 'grabar' para empezar a grabar o 'salir' para finalizar: ").strip().lower()
            if command == "grabar":
                audio_array = mic_manager.record_audio(duration=5)
                transcribed_text = speech_to_text.transcribe(audio_array)
                print(f"Texto transcrito: {transcribed_text}")

                # Convierte el texto transcrito a audio
                text_to_speech_gtts(transcribed_text, lang="es")

            elif command == "salir":
                break
            else:
                print("Comando no reconocido. Usa 'grabar' o 'salir'.")

    finally:
        # Asegúrate de detener el micrófono
        mic_manager.stop_microphone()

if __name__ == "__main__":
    main()
