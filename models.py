import os
from dotenv import load_dotenv
from google import genai

# Cargar API Key
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print(f"{'NOMBRE DEL MODELO':<40} | {'MODALIDADES SOPORTADAS'}")
print("-" * 70)

try:
    # Llamada a la API para listar modelos disponibles
    for model in client.models.list():
        # Filtramos para mostrar los que tienen capacidades de generación de contenido
        if 'generateContent' in model.supported_methods:
            # Mostramos el nombre y las modalidades (texto, imagen, audio, etc.)
            modalities = ", ".join(model.supported_output_modalities) if model.supported_output_modalities else "N/A"
            print(f"{model.name:<40} | {modalities}")
except Exception as e:
    print(f"Error al listar modelos: {e}")