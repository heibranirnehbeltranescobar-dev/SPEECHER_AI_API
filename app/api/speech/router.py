from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from app.core.providers import get_gemini_client

from app.api.speech.service import SpeechService
from app.api.speech.schemas import SpeechRequest

router = APIRouter(
    prefix="/speech",
    tags=["Speech Generation"]
)

@router.post("/generate", response_class=Response)
async def generate_audio_from_text(
    request: SpeechRequest,
    client = Depends(get_gemini_client)
):
    service = SpeechService(client)
    audio_data = service.text_to_audio(request.text)
    
    if audio_data is None:
        raise HTTPException(status_code=500, detail="Error generating audio")
    return Response(content=audio_data, media_type="audio/wav")