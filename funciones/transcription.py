import torch
from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoProcessor

class SpeechToText:
    def __init__(self, model_id="openai/whisper-tiny", device="cpu"):
        """Inicializa el modelo Whisper."""
        self.device = device
        self.model_id = model_id
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id)
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.pipe = pipeline(
            task="automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            device=-1  # CPU
        )
        print(f"Modelo {model_id} cargado en {device}.")

    def transcribe(self, audio_array):
        """Transcribe un array de audio a texto."""
        print("Procesando audio para transcripción...")
        result = self.pipe(audio_array, return_timestamps=False)
        return result["text"]
