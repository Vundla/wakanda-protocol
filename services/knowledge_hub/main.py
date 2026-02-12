"""
Knowledge Hub Service - FastAPI + OpenRouter Integration
Provides AI-powered knowledge management and retrieval services.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import httpx
from typing import Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Knowledge Hub Service",
    description="AI-powered knowledge management and retrieval service using OpenRouter",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    context: Optional[str] = None
    max_tokens: Optional[int] = 1000

class QueryResponse(BaseModel):
    response: str
    model_used: str
    tokens_used: int

class KnowledgeItem(BaseModel):
    id: str
    title: str
    content: str
    category: str
    tags: List[str] = []

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

class OpenRouterClient:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL
        
    async def query_model(self, prompt: str, model: str = "meta-llama/llama-3.1-8b-instruct:free", max_tokens: int = 1000):
        """Query OpenRouter API with the given prompt"""
        if not self.api_key:
            raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://wakanda-protocol.com",
            "X-Title": "Wakanda Protocol Knowledge Hub"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                logger.error(f"OpenRouter API request failed: {e}")
                raise HTTPException(status_code=503, detail="OpenRouter service unavailable")
            except httpx.HTTPStatusError as e:
                logger.error(f"OpenRouter API returned error: {e.response.status_code}")
                raise HTTPException(status_code=e.response.status_code, detail="OpenRouter API error")

# Dependency
def get_openrouter_client():
    return OpenRouterClient()

# In-memory knowledge store (in production, this would be a database)
knowledge_store = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"service": "Knowledge Hub", "status": "healthy", "version": "1.0.0"}

@app.post("/query", response_model=QueryResponse)
async def query_knowledge(
    request: QueryRequest,
    client: OpenRouterClient = Depends(get_openrouter_client)
):
    """Query the knowledge base using AI"""
    try:
        # Enhance prompt with context if provided
        prompt = request.query
        if request.context:
            prompt = f"Context: {request.context}\n\nQuery: {request.query}"
            
        # Query OpenRouter
        response = await client.query_model(prompt, max_tokens=request.max_tokens)
        
        # Extract response data
        content = response["choices"][0]["message"]["content"]
        model_used = response["model"]
        tokens_used = response["usage"]["total_tokens"]
        
        return QueryResponse(
            response=content,
            model_used=model_used,
            tokens_used=tokens_used
        )
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process query")

@app.post("/knowledge", response_model=dict)
async def add_knowledge(item: KnowledgeItem):
    """Add a knowledge item to the store"""
    knowledge_store[item.id] = item.dict()
    return {"message": "Knowledge item added successfully", "id": item.id}

@app.get("/knowledge/{item_id}", response_model=KnowledgeItem)
async def get_knowledge(item_id: str):
    """Retrieve a specific knowledge item"""
    if item_id not in knowledge_store:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    return KnowledgeItem(**knowledge_store[item_id])

@app.get("/knowledge", response_model=List[KnowledgeItem])
async def list_knowledge(category: Optional[str] = None):
    """List all knowledge items, optionally filtered by category"""
    items = list(knowledge_store.values())
    if category:
        items = [item for item in items if item.get("category") == category]
    return [KnowledgeItem(**item) for item in items]

@app.delete("/knowledge/{item_id}")
async def delete_knowledge(item_id: str):
    """Delete a knowledge item"""
    if item_id not in knowledge_store:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    del knowledge_store[item_id]
    return {"message": "Knowledge item deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)