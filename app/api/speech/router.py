from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import Response

from app.core.providers import get_gemini_client

from app.api.speech.service import SpeechService
from app.api.speech.schemas import SpeechRequest

router = APIRouter(
    prefix="/speech",
    tags=["Speech Generation"]
)

@router.post("/tts", response_class=Response)
async def generate_audio_from_text(
    request: SpeechRequest,
    client = Depends(get_gemini_client)
):
    service = SpeechService(client)
    audio_data = service.text_to_audio(request.text)
    
    if audio_data is None:
        raise HTTPException(status_code=500, detail="Error generating audio")
    return Response(content=audio_data, media_type="audio/wav")

@router.post("/stt")
async def generate_text_from_audio(
    file: UploadFile = File(...),
    client = Depends(get_gemini_client)
):

    # Endpoint that receives an audio file and returns the transcription.

    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File provided is not an audio.")

    try:
        # Read file bytes
        audio_content = await file.read()
        
        # Initialize service
        service = SpeechService(client)
        
        # Process transcription
        transcription = service.audio_to_text(audio_content)
        
        if not transcription:
            raise HTTPException(status_code=500, detail="Failed to transcribe audio.")
            
        return {
            "filename": file.filename,
            "transcription": transcription
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))