import os
import httpx
from google import genai
from google.genai import types

class WhatsAppService:
    def __init__(self, ai_client: genai.Client):
        self.ai_client = ai_client
        self.wa_token = os.getenv("META_ACCESS_TOKEN")
        self.wa_phone_id = os.getenv("META_PHONE_NUMBER_ID")
        self.text_model = os.getenv("GEMINI_TEXT_MODE_AI")

    async def process_and_reply(self, sender_phone: str, user_text: str):

        config = types.GenerateContentConfig(
            system_instruction=(
                "Eres un asistente virtual para WhatsApp, especializado en responder preguntas técnicas y de soporte. "
                "Tus respuestas deben ser directas, eficientes, con un tono analítico pero empático. "
                "Usa terminología tecnológica ocasionalmente."
            )
        )
        
        # 2. Think: Gemini generated content based on the user's message and our system instruction
        response = self.ai_client.models.generate_content(
            model=self.text_model,
            contents=user_text,
            config=config
        )
        ai_reply = response.text

        # 3. Text: Playload answer to Meta API 
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": sender_phone,
            "type": "text",
            "text": {"body": ai_reply}
        }

        headers = {
            "Authorization": f"Bearer {self.wa_token}",
            "Content-Type": "application/json"
        }

        url = f"https://graph.facebook.com/v22.0/{self.wa_phone_id}/messages"

        # 4. Enviamos la respuesta a Meta de forma asíncrona
        async with httpx.AsyncClient() as client:
            meta_response = await client.post(url, json=payload, headers=headers)
            if meta_response.status_code in [200, 201]:
                print(f"✅ Mensaje enviado a WhatsApp con éxito!")
            else:
                print(f"❌ Error enviando a Meta (Status {meta_response.status_code}):")
                print(meta_response.text)