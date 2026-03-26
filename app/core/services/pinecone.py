from sentence_transformers import SentenceTransformer
from app.core.providers import get_pinecone_client
import uuid

class PineconeService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2') 
        self.index = get_pinecone_client()

    def _get_embedding(self, text: str) -> list[float]:

        vector = self.model.encode(text)
        return vector.tolist() 

    def save_knowledge(self, text: str, metadata: dict = None):
        vector = self._get_embedding(text)
        vector_id = str(uuid.uuid4())

        final_metadata = metadata or {}
        final_metadata["text"] = text

        record = {
            "id": vector_id,
            "values": vector,
            "metadata": final_metadata
        }
        self.index.upsert(vectors=[record])
        return vector_id

    def search_context(self, query: str, top_k: int = 3) -> str:

        query_vector = self._get_embedding(query)
        
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )

        context_fragments = []
        for match in results.matches:
            text = match.metadata.get("text", "")
            if text:
                context_fragments.append(f"- {text}")
        
        if not context_fragments:
            return "Unable to find useful data."
            
        return "\n".join(context_fragments)