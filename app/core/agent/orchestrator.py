import os
from google.genai import types

from app.core.agent.skills.git_support.schemas import git_skill_declaration
from app.core.agent.skills.quality_standards.schemas import iso_skill_declaration
from app.core.agent.skills.internal_knowledge.schemas import knowledge_skill_declaration

from app.core.agent.skills.git_support.actions import get_git_guide
from app.core.agent.skills.quality_standards.actions import get_quality_standard
from app.core.agent.skills.internal_knowledge.actions import search_internal_knowledge

from app.core.services.ai import AIService

class AgentOrchestrator:

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service 
        
        self.tools = [types.Tool(function_declarations=[

            git_skill_declaration, iso_skill_declaration, knowledge_skill_declaration

        ])]
        self.action_mapping = {
            "get_git_guide": get_git_guide,
            "get_quality_standard": get_quality_standard,
            "search_internal_knowledge": search_internal_knowledge
        }

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

        if is_audio:

            print("🎙️ [Agent] Transcribing incoming audio...")
            transcribed_text = self.ai_service.audio_to_text(input_data)
            if not transcribed_text:
                return {"type": "text", "data": "Lo siento, no pude entender el audio."}
            
            print(f"🗣️ [Agent] User said: {transcribed_text}")
            user_content = types.Content(
                role="user", parts=[types.Part.from_text(text=transcribed_text)]
            )
        else:
            user_content = types.Content(
                role="user", parts=[types.Part.from_text(text=input_data)]
            )

        config = types.GenerateContentConfig(
            tools=self.tools,
            system_instruction=self.system_instruction,
            temperature=0.3
        )

        chat_contents = [user_content]

        response = self.ai_service.generate_text_response(chat_contents, config)

        max_iterations = 10 
        iterations = 0

        while response.function_calls and iterations < max_iterations:
            function_call = response.function_calls[0]
            action_name = function_call.name
            action_args = function_call.args
            print(f"🛠️ [Agent] Executing tool: {action_name} | Args: {action_args}")

            if action_name in self.action_mapping:
                action_result = self.action_mapping[action_name](**action_args)
                
                chat_contents.append(response.candidates[0].content)
                chat_contents.append(
                    types.Content(role="user", parts=[types.Part.from_function_response(name=action_name, response={"result": action_result})])
                )
                
                response = self.ai_service.generate_text_response(chat_contents, config)
            
            iterations += 1

        try:
            final_text = response.text
            if not final_text:
                final_text = "Lo siento, tuve un problema interno al generar la respuesta."
        except ValueError:
            final_text = "Lo siento, no pude formular una respuesta con esa información."

        print(f"📝 [Agent] RAW AI Text: {final_text}")
        
        wants_audio_output = is_audio 
        
        if "[AUDIO]" in final_text:
            wants_audio_output = True
            final_text = final_text.replace("[AUDIO]", "").strip()
            print("🔀 [Agent] Override triggered: AI chose AUDIO output.")
            
        elif "[TEXT]" in final_text:
            wants_audio_output = False
            final_text = final_text.replace("[TEXT]", "").strip()
            print("🔀 [Agent] Override triggered: AI chose TEXT output.")

        if not final_text:
            final_text = "Aquí tienes la información solicitada."

        print(f"🧠 [Agent] Final Output Format: {'AUDIO' if wants_audio_output else 'TEXT'}")

        if wants_audio_output:
            try:

                pcm_data = self.ai_service.text_to_audio(final_text)
                if pcm_data:
                    wav_bytes = self.ai_service.create_wav_header(len(pcm_data)) + pcm_data
                    opus_bytes = self.ai_service.wav_to_opus(wav_bytes)
                    return {"type": "audio", "data": opus_bytes}
                raise Exception("TTS returned empty bytes")
            except Exception as e:
                print(f"❌ [Agent] TTS failed, falling back to text: {e}")
                return {"type": "text", "data": final_text}
        else:
            return {"type": "text", "data": final_text}