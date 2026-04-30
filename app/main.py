"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.routes import router

app = FastAPI(title="RAGSense API")
app.include_router(auth_router)   # /api/init, /api/create_user, /api/login
app.include_router(router)        # /rag/query, /rag/documents/upload
app.state.description_ = ""


@app.get("/")
async def root():
    """Root endpoint to verify API is running."""
    return {"message": "RAGSense API is running"}
