from gtts import gTTS
import os

def text_to_speech_gtts(text, lang="es"):
    """Convierte texto a voz usando gTTS."""
    try:
        print("Convirtiendo texto a audio...")
        tts = gTTS(text=text, lang=lang)
        tts.save("output.mp3")  # Guardar como archivo
        os.system("start output.mp3")  # Reproducir el archivo (Windows)
        print("Audio generado y reproducido.")
    except Exception as e:
        print(f"Error al convertir texto a audio: {e}")
