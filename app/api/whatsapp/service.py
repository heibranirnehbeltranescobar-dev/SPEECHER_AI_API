import os
import httpx
from google import genai

# Import the new orchestrator
from app.agent.orchestrator import AgentOrchestrator

class WhatsAppService:
    def __init__(self, ai_client: genai.Client):
        self.ai_client = ai_client
        self.wa_token = os.getenv("META_ACCESS_TOKEN")
        self.wa_phone_id = os.getenv("META_PHONE_NUMBER_ID")
        
        self.messages_url = f"https://graph.facebook.com/v22.0/{self.wa_phone_id}/messages"
        self.base_headers = {
            "Authorization": f"Bearer {self.wa_token}",
            "Content-Type": "application/json"
        }
        
        self.agent = AgentOrchestrator(ai_client)

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

    async def get_media_url(self, media_id: str) -> str:
        # Gets the download URL for the media file from Meta API.
        url = f"https://graph.facebook.com/v22.0/{media_id}"
        headers = {"Authorization": f"Bearer {self.wa_token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                raise Exception(f"Error obteniendo URL de media: {resp.text}")
            return resp.json().get("url")

    async def download_media(self, media_url: str) -> bytes:
        # Downloads the binary bytes of the audio file.
        headers = {"Authorization": f"Bearer {self.wa_token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(media_url, headers=headers)
            if resp.status_code != 200:
                raise Exception("Error descargando archivo de audio")
            return resp.content

    async def upload_audio_to_meta(self, audio_bytes: bytes) -> str:
        # Uploads the generated audio back to Meta's servers
        url = f"https://graph.facebook.com/v22.0/{self.wa_phone_id}/media"
        headers = {"Authorization": f"Bearer {self.wa_token}"}
        data = {"messaging_product": "whatsapp"}
        files = {"file": ("audio.ogg", audio_bytes, "audio/ogg")}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data, files=files)
            if response.status_code == 200:
                media_id = response.json().get("id")
                return media_id
            raise Exception(f"Failed to upload audio to Meta: {response.text}")

    def build_audio_payload(self, sender_phone: str, message_id: str, media_id: str) -> dict:
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
            "text": {"body": "Lo siento, tuve un problema técnico al procesar tu solicitud."}
        }
        await self.send_request(payload)

    async def process_audio_and_reply(self, sender_phone: str, audio_id: str, message_id: str):
        """ Flow for incoming Voice Notes: Download -> Delegate to Agent -> Send Media/Text """
        try:
            await self.send_typing_indicator(message_id)

            # 1. Fetch raw OGG bytes from Meta
            url = await self.get_media_url(audio_id)
            audio_bytes = await self.download_media(url)
            
            print("🔊 [WhatsAppService] Audio downloaded, passing directly to Agent...")

            # 2. Delegate entire logic to Orchestrator
            agent_response = await self.agent.process_interaction(input_data=audio_bytes, is_audio=True)

            # 3. Route response based on what the Agent returned (Dynamic formatting)
            if agent_response["type"] == "audio":
                print("🔊 [WhatsAppService] Agent chose Audio. Uploading to Meta...")
                media_id = await self.upload_audio_to_meta(agent_response["data"])
                payload = self.build_audio_payload(sender_phone, message_id, media_id)
            else:
                print("📝 [WhatsAppService] Agent chose Text override.")
                payload = self.build_text_payload(sender_phone, message_id, agent_response["data"])

            response = await self.send_request(payload)
            if response.status_code in [200, 201]:
                print("✅ [WhatsAppService] Audio flow response sent successfully.")

        except Exception as e:
            print(f"❌ [WhatsAppService] Error in audio flow: {e}")
            await self.send_fallback_message(sender_phone, message_id)

    async def process_and_reply(self, sender_phone: str, user_text: str, message_id: str):
        """ Flow for incoming Text Messages: Delegate to Agent -> Send Text/Media """
        try:
            print(f"💬 [WhatsAppService] Analyzing text: {user_text}")
            await self.send_typing_indicator(message_id)

            # 1. Delegate text to the Orchestrator
            agent_response = await self.agent.process_interaction(input_data=user_text, is_audio=False)

            # 2. Check the format the Agent decided to output (Dynamic formatting)
            if agent_response["type"] == "audio":
                print("🔊 [WhatsAppService] Agent chose Audio for Text input. Uploading to Meta...")
                media_id = await self.upload_audio_to_meta(agent_response["data"])
                payload = self.build_audio_payload(sender_phone, message_id, media_id)
            else:
                print("📝 [WhatsAppService] Agent chose Text output.")
                payload = self.build_text_payload(sender_phone, message_id, agent_response["data"])
            
            # 3. Send the response to WhatsApp
            response = await self.send_request(payload)
            if response.status_code in [200, 201]:
                print("✅ [WhatsAppService] Text flow response sent successfully.")

        except Exception as e:
            print(f"❌ [WhatsAppService] Error in text flow: {e}")
            await self.send_fallback_message(sender_phone, message_id)