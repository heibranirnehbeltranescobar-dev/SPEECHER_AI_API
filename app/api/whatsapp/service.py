import os
import httpx
from google import genai
from google.genai import types
from app.api.speech.service import SpeechService

class WhatsAppService:
    def __init__(self, ai_client: genai.Client):
        self.ai_client = ai_client
        self.wa_token = os.getenv("META_ACCESS_TOKEN")
        self.wa_phone_id = os.getenv("META_PHONE_NUMBER_ID")
        self.text_model = os.getenv("GEMINI_TEXT_MODE_AI")
        self.speech_service = SpeechService(ai_client)

        self.messages_url = f"https://graph.facebook.com/v22.0/{self.wa_phone_id}/messages"
        self.base_headers = {
            "Authorization": f"Bearer {self.wa_token}",
            "Content-Type": "application/json"
        }

    async def send_request(self, payload: dict) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.messages_url,
                json=payload,
                headers=self.base_headers
            )
            if response.status_code not in [200, 201]:
                print(f"Meta API error: {response.text}")
            return response

    async def send_typing_indicator(self, message_id: str):
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
            "typing_indicator": {"type": "text"}
        }
        await self.send_request(payload)

    def wants_audio(self, user_text: str) -> bool:
        config = types.GenerateContentConfig(
            system_instruction=(
                "Analyze the user's message and determine if they are explicitly "
                "or implicitly asking for a voice message or audio response. "
                "Reply STRICTLY with 'yes' or 'no'. No punctuation or additional text."
            ),
            temperature=0.0
        )
        try:
            response = self.ai_client.models.generate_content(
                model=self.text_model,
                contents=user_text,
                config=config
            )
            return response.text.strip().lower() == "yes"
        except Exception as e:
            print(f"Intent classification error: {e}")
            return False

    def generate_text_reply(self, user_text: str, is_audio_requested: bool) -> str:
        prompt_context = (
            "You are a virtual assistant for WhatsApp, specialized in technical support. "
            "Your answers must be direct, concise, and efficient, with an analytical yet empathetic tone. "
            "Use technical terminology occasionally."
        )

        if is_audio_requested:
            prompt_context += (
                " IMPORTANT: Your response will be read aloud by a TTS system. "
                "Respond naturally, conversationally, using full words and NO asterisks, emojis, hashtags, or bullet points."
            )

        config = types.GenerateContentConfig(system_instruction=prompt_context)
        response = self.ai_client.models.generate_content(
            model=self.text_model,
            contents=user_text,
            config=config
        )
        return response.text

    async def upload_audio_to_meta(self, audio_bytes: bytes) -> str:
        url = f"https://graph.facebook.com/v22.0/{self.wa_phone_id}/media"
        headers = {"Authorization": f"Bearer {self.wa_token}"}
        data = {"messaging_product": "whatsapp"}
        files = {"file": ("response.wav", audio_bytes, "audio/wav")}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data, files=files)
            if response.status_code == 200:
                media_id = response.json().get("id")
                return media_id
            raise Exception(f"Failed to upload audio to Meta: {response.text}")

    async def build_audio_payload(self, sender_phone: str, message_id: str, ai_reply: str) -> dict:

        wav_bytes = self.speech_service.text_to_audio(ai_reply)
        if not wav_bytes:
            raise Exception("Audio generation failed.")

        # 2. Convertir a OGG usando nuestra nueva función
        ogg_bytes = self.speech_service.wav_to_opus(wav_bytes)

        media_id = await self.upload_audio_to_meta(ogg_bytes)
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": sender_phone,
            "type": "audio",
            "context": {"message_id": message_id},
            "audio": {"id": media_id}
        }

    def build_text_payload(self, sender_phone: str, message_id: str, ai_reply: str) -> dict:
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": sender_phone,
            "type": "text",
            "context": {"message_id": message_id},
            "text": {"body": ai_reply}
        }

    async def send_fallback_message(self, sender_phone: str, message_id: str):
        payload = {
            "messaging_product": "whatsapp",
            "to": sender_phone,
            "type": "text",
            "context": {"message_id": message_id},
            "text": {"body": "Lo siento, tengo problemas para cumplir con lo solicitado :c"}
        }
        await self.send_request(payload)

    async def process_and_reply(self, sender_phone: str, user_text: str, message_id: str):
        try:
            is_audio_requested = self.wants_audio(user_text)
            await self.send_typing_indicator(message_id)

            ai_reply = self.generate_text_reply(user_text, is_audio_requested)

            if is_audio_requested:
                payload = await self.build_audio_payload(sender_phone, message_id, ai_reply)
            else:
                payload = self.build_text_payload(sender_phone, message_id, ai_reply)

            response = await self.send_request(payload)
            if response.status_code in [200, 201]:
                print("Response sent to WhatsApp successfully.")

        except Exception as e:
            print(f"Processing flow error: {e}")
            await self.send_fallback_message(sender_phone, message_id)