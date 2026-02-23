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

    async def process_and_reply(self, sender_phone: str, user_text: str, message_id: str):

        headers = {
            "Authorization": f"Bearer {self.wa_token}",
            "Content-Type": "application/json"
        }

        url = f"https://graph.facebook.com/v22.0/{self.wa_phone_id}/messages"

        async with httpx.AsyncClient() as client:

            typing_payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id,
                "typing_indicator": {
                    "type": "text"
                }
            }

            await client.post(url, json=typing_payload, headers=headers)

            config = types.GenerateContentConfig(
                system_instruction=(
                    "Eres un asistente virtual para WhatsApp, especializado en responder preguntas técnicas y de soporte. "
                    "Tus respuestas deben ser directas, consisas, eficientes, con un tono analítico pero empático. "
                    "Usa terminología tecnológica ocasionalmente."
                )
            )
            
            try:
                response = self.ai_client.models.generate_content(
                    model=self.text_model,
                    contents=user_text,
                    config=config
                )
                final_reply = response.text

            except Exception as e:
                print(f"⚠️ Error en Gemini: {e}")
                final_reply = "Lo siento, tuve un problema procesando tu mensaje. ¿Podrías intentar decírmelo de otra forma? 🤖"
            reply_payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "context": {
                    "message_id": message_id
                },
                "to": sender_phone,
                "type": "text",
                "text": {"body": final_reply}
            }

            meta_response = await client.post(url, json=reply_payload, headers=headers)
            if meta_response.status_code in [200, 201]:
                print(f"✅ Mensaje enviado a WhatsApp con éxito!")
            else:
                print(f"❌ Error enviando a Meta (Status {meta_response.status_code}):")
                print(meta_response.text)