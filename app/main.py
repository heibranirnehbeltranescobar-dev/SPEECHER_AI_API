from fastapi import FastAPI

from app.api.whatsapp import router as whatsapp_router
from app.api.knowledge import router as knowledge_router

app = FastAPI(title="SPEECHER_API")

app.include_router(whatsapp_router.router)
app.include_router(knowledge_router.router)