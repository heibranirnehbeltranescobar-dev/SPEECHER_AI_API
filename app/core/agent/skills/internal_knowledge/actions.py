from app.core.services.pinecone import PineconeService 

pinecone_service = PineconeService()

def search_internal_knowledge(query: str) -> str:
    print(f"📚 [Skill] Consultando Pinecone para: '{query}'")
    
    context = pinecone_service.search_context(query)
    
    return context