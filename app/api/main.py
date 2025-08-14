"""
StackGuide FastAPI Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="StackGuide API",
    description="Local-first AI Knowledge Assistant",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "StackGuide API is running!"}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "StackGuide API"}

@app.get("/api/query")
async def query(q: str):
    """Query endpoint (placeholder)."""
    return {
        "query": q,
        "answer": "This is a placeholder response. Query processing coming soon!",
        "citations": [],
        "confidence": 0.0
    }
