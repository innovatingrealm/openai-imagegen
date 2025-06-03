from fastapi import APIRouter, HTTPException
from ..models import ImageGenerationRequest, ImageResponse
from ..services.openai_service import OpenAIImageService

router = APIRouter()
service = OpenAIImageService()

@router.post("/generate", response_model=ImageResponse)
async def generate_image(request: ImageGenerationRequest):
    """
    Generate image from text prompt
    
    This endpoint supports:
    - Text-to-image generation
    - Multiple models (DALL-E 2, DALL-E 3, GPT-Image-1)
    - Various sizes and qualities
    - Multiple images in one request
    """
    result = await service.generate_image(request)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ImageResponse(**result)