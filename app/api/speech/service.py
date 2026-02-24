import os
import struct
from google.genai import types
import subprocess

class SpeechService:
    # Recibimos el cliente inyectado en el constructor
    def __init__(self, client):
        self.client = client
        self.voice_model = os.getenv("GEMINI_VOICE_MODE_AI")

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
            model=self.voice_model,
            contents=text,
            config=config
        )
        
        audio_chunks = [part.inline_data.data for part in response.candidates[0].content.parts if part.inline_data]
        
        if not audio_chunks:
            return None
            
        pcm_data = b"".join(audio_chunks)
        return self.create_wav_header(len(pcm_data)) + pcm_data

    def wav_to_opus(self, wav_bytes: bytes) -> bytes:
            # Converts WAV bytes to OGG Opus bytes using FFmpeg directly.
            command = [
                "ffmpeg",
                "-i", "pipe:0",
                "-c:a", "libopus",
                "-f", "ogg",
                "pipe:1"
            ]
            
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            ogg_bytes, stderr_output = process.communicate(input=wav_bytes)
            
            if process.returncode != 0:
                error_msg = stderr_output.decode("utf-8", errors="ignore")
                print(f"FFmpeg error: {error_msg}")
                raise Exception("Failed to convert WAV to OGG Opus via FFmpeg.")
                
            return ogg_bytes