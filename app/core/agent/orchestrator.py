import os
from google import genai
from google.genai import types

from app.core.agent.skills.git_support.schemas import git_skill_declaration
from app.core.agent.skills.quality_standards.schemas import iso_skill_declaration
from app.core.agent.skills.git_support.actions import get_git_guide
from app.core.agent.skills.quality_standards.actions import get_quality_standard
from app.api.speech.service import SpeechService

class AgentOrchestrator:
    def __init__(self, ai_client: genai.Client):
        self.ai_client = ai_client
        self.text_model = os.getenv("GEMINI_TEXT_MODEL_AI")
        self.voice_model = os.getenv("GEMINI_VOICE_MODEL_AI")
        self.speech_service = SpeechService(ai_client)
        
        self.tools = [types.Tool(function_declarations=[git_skill_declaration, iso_skill_declaration])]
        self.action_mapping = {
            "get_git_guide": get_git_guide,
            "get_quality_standard": get_quality_standard
        }

        # UPDATE: New routing rules for the AI
        self.system_instruction = (
            "Eres el asistente virtual oficial de soporte para estudiantes de ingeniería. "
            "Resuelve dudas usando las herramientas proporcionadas. "
            "REGLAS DE FORMATO DE RESPUESTA: "
            "1. Por defecto, responde en el mismo formato que el usuario. "
            "2. Si el usuario te escribe por texto, pero te pide explícitamente un audio o nota de voz, DEBES iniciar tu respuesta exactamente con la etiqueta '[AUDIO]'. "
            "3. Si el usuario te envía un audio, pero te pide código, comandos, o dice 'escríbelo'/'mándalo por texto', DEBES iniciar tu respuesta exactamente con la etiqueta '[TEXT]'. "
            "4. Si se va a retornar un audio, este debe ser lo más corto y conciso posible a no ser que el usuario solicite lo contario. "
            "JAMÁS incluyas estas etiquetas si no hay una petición explícita de cambio de formato."
        )

    async def process_interaction(self, input_data: str | bytes, is_audio: bool = False) -> dict:
        print(f"🤖 [Agent] Processing interaction. Input is Audio? {is_audio}")

        # 1. Prepare Content
        if is_audio:
            user_content = types.Content(
                role="user", 
                parts=[
                    types.Part.from_text(text="Please listen to this student's audio message:"),
                    types.Part.from_bytes(data=input_data, mime_type="audio/ogg")
                ]
            )
        else:
            user_content = types.Content(
                role="user", parts=[types.Part.from_text(text=input_data)]
            )

        # 2. Config & Call
        config = types.GenerateContentConfig(
            tools=self.tools,
            system_instruction=self.system_instruction,
            temperature=0.3
        )

        chat_contents = [user_content]

        response = self.ai_client.models.generate_content(
            model=self.text_model,
            contents=[user_content],
            config=config
        )

        metadata = response.usage_metadata
        if metadata:
            print(f"\n---------------Texto----------------------")
            #print(metadata)
            print(f"Input Tokens: {metadata.prompt_token_count}")
            print(f"Output Tokens: {metadata.candidates_token_count}")
            print(f"\nTotal Tokens: {metadata.total_token_count}")
            print(f"-------------------------------------\n")

        max_iterations = 10 # Límite de seguridad para que no investigue infinitamente
        iterations = 0

        # 3. Handle Tool Calls
        while response.function_calls and iterations < max_iterations:
            function_call = response.function_calls[0]
            action_name = function_call.name
            action_args = function_call.args
            print(f"🛠️ [Agent] Executing tool: {action_name} | Args: {action_args}")

            if action_name in self.action_mapping:
                action_result = self.action_mapping[action_name](**action_args)
                
                # 1. Guardamos la petición de la herramienta (mantiene el thought_signature)
                chat_contents.append(response.candidates[0].content)
                
                # 2. Guardamos la respuesta de nuestra función con los datos
                chat_contents.append(
                    types.Content(role="user", parts=[types.Part.from_function_response(name=action_name, response={"result": action_result})])
                )
                
                # 3. La IA vuelve a pensar con el historial actualizado
                response = self.ai_client.models.generate_content(
                    model=self.text_model,
                    contents=chat_contents,
                    config=config
                )
            
            iterations += 1

        # Extracción segura de texto (Salvavidas)
        try:
            final_text = response.text
            if not final_text:
                final_text = "Lo siento, tuve un problema interno al generar la respuesta."
        except ValueError:
            # El SDK de Gemini lanza ValueError si el modelo fue filtrado o no devuelve texto
            final_text = "Lo siento, no pude formular una respuesta con esa información."

        print(f"📝 [Agent] RAW AI Text: {final_text}")
        
        # ==========================================
        # 4. INTELLIGENT ROUTING LOGIC
        # ==========================================
        
        # Default behavior: mirror the input format
        wants_audio_output = is_audio 
        
        # Búsqueda flexible de etiquetas por si la IA agrega símbolos Markdown
        if "[AUDIO]" in final_text:
            wants_audio_output = True
            final_text = final_text.replace("[AUDIO]", "").strip()
            print("🔀 [Agent] Override triggered: AI chose AUDIO output.")
            
        elif "[TEXT]" in final_text:
            wants_audio_output = False
            final_text = final_text.replace("[TEXT]", "").strip()
            print("🔀 [Agent] Override triggered: AI chose TEXT output.")

        # Salvavidas Anti-Errores de Meta: Evitar un text['body'] vacío
        if not final_text:
            final_text = "Aquí tienes la información solicitada."

        print(f"🧠 [Agent] Final Output Format: {'AUDIO' if wants_audio_output else 'TEXT'}")

        # 5. Process Output Route
        if wants_audio_output:
            try:
                pcm_data = self.speech_service.text_to_audio(final_text)
                if pcm_data:
                    wav_bytes = self.speech_service.create_wav_header(len(pcm_data)) + pcm_data
                    opus_bytes = self.speech_service.wav_to_opus(wav_bytes)
                    return {"type": "audio", "data": opus_bytes}
                raise Exception("TTS returned empty bytes")
            except Exception as e:
                print(f"❌ [Agent] TTS failed, falling back to text: {e}")
                return {"type": "text", "data": final_text}
        else:
            return {"type": "text", "data": final_text}