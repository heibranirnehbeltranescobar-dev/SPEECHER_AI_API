import os
from fastapi import APIRouter, Depends, Request, HTTPException, Query, BackgroundTasks
from fastapi.responses import PlainTextResponse
from app.core.providers import get_gemini_client
from app.api.whatsapp.service import WhatsAppService

router = APIRouter(prefix="/webhook", tags=["WhatsApp Integration"])

@router.get("/")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    # Meta Webhook Verification Endpoint
    verify_token = os.getenv("META_WEBHOOK_VERIFY_TOKEN")
    
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Token de verificación inválido")

@router.post("/")
async def receive_message(
    request: Request, 
    background_tasks: BackgroundTasks,
    client = Depends(get_gemini_client)
):
    body = await request.json()

    try:
        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if messages:
            message = messages[0]
            sender_phone = message.get("from")
            message_id = message.get("id")
            service = WhatsAppService(client)

            # CASO 1: El usuario envía TEXTO
            if message.get("type") == "text":
                user_text = message.get("text", {}).get("body")
                background_tasks.add_task(
                    service.process_text_and_reply, 
                    sender_phone, user_text, message_id
                )

            # CASO 2: El usuario envía AUDIO (Mensaje de voz)
            elif message.get("type") == "audio":
                audio_id = message.get("audio", {}).get("id")
                background_tasks.add_task(
                    service.process_audio_and_reply, 
                    sender_phone, audio_id, message_id
                )

        return {"status": "success"}

    except Exception as e:
        print(f"Error processing the Webhook: {e}")
        return {"status": "error"}