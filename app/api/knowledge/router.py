from fastapi import APIRouter, HTTPException
from app.api.knowledge.schemas import InsertKnowledgeRequest, QueryKnowledgeRequest

from app.core.services.pinecone import PineconeService 

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge Base (Pinecone)"]
)

pinecone_service = PineconeService()

@router.post("/", summary="Insert Knowledge")
async def insert_knowledge(request: InsertKnowledgeRequest):

    try:
        vector_id = pinecone_service.save_knowledge(
            text=request.text, 
            metadata=request.metadata
        )
        return {
            "status": "success", 
            "vector_id": vector_id, 
            "message": "Knowledge save successfully."
        }
    except Exception as e:
        print(f"❌ Error insertando en Pinecone: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", summary="Search Knowledge")
async def query_knowledge(request: QueryKnowledgeRequest):

    try:
        context = pinecone_service.search_context(
            query=request.query, 
            top_k=request.top_k
        )
        return {
            "status": "success", 
            "query": request.query,
            "context": context
        }
    except Exception as e:
        print(f"❌ Error consultando Pinecone: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")