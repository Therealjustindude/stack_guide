"""
Simple FastAPI server for LLM service
"""

from fastapi import FastAPI

app = FastAPI(title="StackGuide LLM Service")

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "StackGuide LLM"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "StackGuide LLM Service is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
