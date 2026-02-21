from fastapi import FastAPI
from app.api.speech import router as speech_router

app = FastAPI(title="SPEECHER_API")

app.include_router(speech_router.router)