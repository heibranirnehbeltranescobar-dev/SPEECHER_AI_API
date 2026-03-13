import os
import struct
from google.genai import types
import subprocess
from app.api.speech.schemas import TranscriptionResponse

class SpeechService:
    # Recibimos el cliente inyectado en el constructor
    def __init__(self, client):
        self.client = client
        self.voice_model = os.getenv("GEMINI_VOICE_MODEL_AI")
        self.text_model = os.getenv("GEMINI_TEXT_MODEL_AI")

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

    def audio_to_text(self, audio_bytes: bytes) -> str:

        # Converts audio bytes to text using FFmpeg for normalization 
        # and Gemini for Speech-to-Text in English.

        try:
            # Normalize audio to WAV 16kHz mono using FFmpeg (in-memory)
            command = [
                "ffmpeg",
                "-i", "pipe:0",        # Input from stdin
                "-ar", "16000",        # sample rate
                "-ac", "1",            # mono
                "-f", "wav",           # format
                "pipe:1"               # Output to stdout
            ]
            
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            wav_data, stderr = process.communicate(input=audio_bytes)
            
            if process.returncode != 0:
                print(f"FFmpeg STT Error: {stderr.decode()}")
                return None

            # Send to Gemini for transcription
            response = self.client.models.generate_content(
                model=self.text_model,
                contents=[
                    "Transcribe this audio accurately to text in the language o languages the person is speaking in the audio.",
                    types.Part.from_bytes(data=wav_data, mime_type="audio/wav")
                ]
            )
            
            return response.text.strip()
            
        except Exception as e:
            print(f"STT Processing Error: {e}")
            return None

    def wav_to_opus(self, wav_bytes: bytes) -> bytes:
            # Converts WAV bytes to OGG Opus bytes using FFmpeg directly.
            command = [
                "ffmpeg",
                "-i", "pipe:0",
                "-c:a", "libopus",
                "-b:a", "64k",
                "-vbr", "on",
                "-f", "opus",
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