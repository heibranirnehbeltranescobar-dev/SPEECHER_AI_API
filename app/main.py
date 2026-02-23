from fastapi import FastAPI
from app.api.speech import router as speech_router
from app.api.whatsapp import router as whatsapp_router

app = FastAPI(title="SPEECHER_API")

app.include_router(speech_router.router)
app.include_router(whatsapp_router.router)