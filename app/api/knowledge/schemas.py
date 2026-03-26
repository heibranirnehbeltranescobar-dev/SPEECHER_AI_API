from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class InsertKnowledgeRequest(BaseModel):
    text: str = Field(..., description="The text or fragment to vectorize and save.")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Optional Metadata (ej. {'source': 'manual_v1', 'category': 'handbook'})"
    )

class QueryKnowledgeRequest(BaseModel):
    query: str = Field(..., description="Question or phrase to search.")
    top_k: int = Field(default=3, description="Relevant fragments to return.")