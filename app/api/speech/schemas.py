from pydantic import BaseModel, Field
from typing import TypedDict

class SpeechRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, example="Hello, how's it going?")

class TranscriptionResponse(TypedDict):
    filename: str
    transcription: str