from fastapi import APIRouter
from datetime import datetime
from ..models import HealthResponse
from ..services.openai_service import OpenAIImageService

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        service = OpenAIImageService()
        openai_status = "healthy" if await service.check_api_status() else "unhealthy"
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            openai_status=openai_status
        )
    except Exception as e:
        return HealthResponse(
            status="error",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            openai_status="error"
        )