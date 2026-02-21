import struct
from google.genai import types

class SpeechService:
    # Recibimos el cliente inyectado en el constructor
    def __init__(self, client):
        self.client = client

    def create_wav_header(self, data_length, sample_rate=24000):
        return struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF", 36 + data_length, b"WAVE", b"fmt ",
            16, 1, 1, sample_rate, sample_rate * 2, 2, 16,
            b"data", data_length
        )

    def text_to_audio(self, text: str) -> bytes:
        config = types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
                )
            )
        )
        
        response = self.client.models.generate_content(
            model="gemini-2.5-pro-preview-tts",
            contents=text,
            config=config
        )
        
        audio_chunks = [part.inline_data.data for part in response.candidates[0].content.parts if part.inline_data]
        
        if not audio_chunks:
            return None
            
        pcm_data = b"".join(audio_chunks)
        return self.create_wav_header(len(pcm_data)) + pcm_data