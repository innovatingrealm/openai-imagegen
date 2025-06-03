from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="OpenAI Image Generation API",
    description="A comprehensive API for OpenAI image generation, editing, and variations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from .routers import generation, health, reference

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(generation.router, prefix="/api/v1/images", tags=["Image Generation"])
app.include_router(reference.router, prefix="/api/v1/images", tags=["Reference Generation"])

@app.get("/")
async def root():
    return {
        "message": "OpenAI Image Generation API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "running"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=False
    )