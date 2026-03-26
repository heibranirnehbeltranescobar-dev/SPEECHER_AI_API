import os
import struct
import subprocess

from google.genai import types

class AIService:
    def __init__(self, client):
        self.client = client
        self.voice_model = os.getenv("GEMINI_VOICE_MODEL_AI")
        self.text_model = os.getenv("GEMINI_TEXT_MODEL_AI")

    def generate_text_response(self, contents: list, config: types.GenerateContentConfig):

        response = self.client.models.generate_content(
            model=self.text_model,
            contents=contents,
            config=config
        )

        metadata = response.usage_metadata
        if metadata:
            print(f"\n---------------TEXT----------------------")
            print(f"Input Tokens: {metadata.prompt_token_count}")
            print(f"Output Tokens: {metadata.candidates_token_count}")
            print(f"Total Tokens: {metadata.total_token_count}")
            print(f"------------------------------------------\n")

        return response

    def create_wav_header(self, data_length, sample_rate=24000):
        return struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF", 36 + data_length, b"WAVE", b"fmt ",
            16, 1, 1, sample_rate, sample_rate * 2, 2, 16,
            b"data", data_length
        )

    def text_to_audio(self, text: str) -> bytes | None:
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

        metadata = response.usage_metadata
        if metadata:
            print(f"\n---------------AUDIO----------------------")
            print(f"Input Tokens: {metadata.prompt_token_count}")
            print(f"Output Tokens: {metadata.candidates_token_count}")
            print(f"Total Tokens: {metadata.total_token_count}")
            print(f"------------------------------------------\n")

        audio_chunks = [part.inline_data.data for part in response.candidates[0].content.parts if part.inline_data]
        
        if not audio_chunks:
            return None
            
        pcm_data = b"".join(audio_chunks)
        return self.create_wav_header(len(pcm_data)) + pcm_data

    def audio_to_text(self, audio_bytes: bytes) -> str | None:
        try:
            command = [
                "ffmpeg", "-i", "pipe:0", "-ar", "16000", "-ac", "1", "-f", "wav", "pipe:1"
            ]
            
            process = subprocess.Popen(
                command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            
            wav_data, stderr = process.communicate(input=audio_bytes)
            
            if process.returncode != 0:
                print(f"FFmpeg STT Error: {stderr.decode()}")
                return None

            response = self.generate_text_response([
                "Transcribe this audio accurately to text in the language o languages the person is speaking in the audio.",
                types.Part.from_bytes(data=wav_data, mime_type="audio/wav")
            ], None)
            
            return response.text.strip()
            
        except Exception as e:
            print(f"STT Processing Error: {e}")
            return None

    def wav_to_opus(self, wav_bytes: bytes) -> bytes:
        command = [
            "ffmpeg", "-i", "pipe:0", "-c:a", "libopus", "-b:a", "64k", "-vbr", "on", "-f", "opus", "pipe:1"
        ]
        
        process = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        ogg_bytes, stderr_output = process.communicate(input=wav_bytes)
        
        if process.returncode != 0:
            error_msg = stderr_output.decode("utf-8", errors="ignore")
            print(f"FFmpeg error: {error_msg}")
            raise Exception("Failed to convert WAV to OGG Opus via FFmpeg.")
            
        return ogg_bytes