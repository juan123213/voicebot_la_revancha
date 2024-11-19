from gtts import gTTS
import pygame
import os

def text_to_speech_gtts(text, lang="es"):
    """Convierte texto a voz usando gTTS, reproduce el audio y elimina el archivo."""
    try:
        print("Convirtiendo texto a audio...")
        tts = gTTS(text=text, lang=lang)
        audio_file = "output.mp3"  # Archivo temporal
        tts.save(audio_file)  # Guardar como archivo temporal

        print("Reproduciendo audio...")
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        # Esperar hasta que termine la reproducción
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Pequeña espera para evitar bloquear el CPU
        
        # Detener el mixer y liberar el archivo
        pygame.mixer.music.stop()
        pygame.mixer.quit()

        # Eliminar el archivo temporal
        os.remove(audio_file)
        print("Archivo temporal eliminado.")
    except Exception as e:
        print(f"Error al convertir texto a audio: {e}")
