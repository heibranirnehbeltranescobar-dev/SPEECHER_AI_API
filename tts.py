import os
import struct
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Cargar configuración desde el archivo .env
load_dotenv()

# Inicializar cliente con la API Key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def create_wav_header(data_length, sample_rate=24000):
    """Genera el encabezado RIFF/WAVE para archivos PCM de 16-bit."""
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36 + data_length, b"WAVE", b"fmt ",
        16, 1, 1, sample_rate, sample_rate * 2, 2, 16,
        b"data", data_length
    )
    return header

def generate_audio():
    print("Conectando con la IA para generar audio en español...")
    
    # CAMBIO CLAVE: Usamos el modelo experimental que tiene habilitado el TTS nativo
    model_id = "gemini-2.5-pro-preview-tts" 

    config = types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Puck" # Voz masculina clara
                )
            )
        )
    )

    # Prompt optimizado para evitar errores de interpretación de modalidad
    prompt = "Genera un audio de alta calidad diciendo: 'Hola, esta es una prueba de generación de voz en español desde Python.'"

    try:
        audio_chunks = []
        
        # Consumir el stream de audio
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=config
        )

        # En la versión no-stream, el audio suele venir en la primera parte
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                audio_chunks.append(part.inline_data.data)
                print(".", end="", flush=True)

        if audio_chunks:
            print("\nEnsamblando archivo...")
            pcm_data = b"".join(audio_chunks)
            wav_header = create_wav_header(len(pcm_data))
            
            output_file = "audio.wav"
            with open(output_file, "wb") as f:
                f.write(wav_header)
                f.write(pcm_data)
            
            print(f"¡Éxito! Archivo guardado en: {os.path.abspath(output_file)}")
        else:
            print("\nEl modelo no devolvió datos de audio. Intenta cambiar el modelo a 'gemini-2.0-flash-lite-preview-02-05'")

    except Exception as e:
        print(f"\nError detectado: {e}")

if __name__ == "__main__":
    generate_audio()