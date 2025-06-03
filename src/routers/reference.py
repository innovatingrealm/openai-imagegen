from fastapi import APIRouter, HTTPException
from ..models import ReferenceGenerationRequest, ImageResponse
from ..services.openai_service import OpenAIImageService

router = APIRouter()
service = OpenAIImageService()

@router.post("/generate-with-reference", response_model=ImageResponse)
async def generate_with_reference(request: ReferenceGenerationRequest):
    """
    Generate image using reference image URLs with GPT-Image-1
    
    This endpoint:
    - Uses GPT-Image-1 for best reference understanding
    - Accepts single or multiple reference image URLs
    - Downloads images automatically
    - Perfect for n8n workflows
    
    Example usage:
    {
        "prompt": "The seer fighting Lucien while victor watches",
        "image_urls": ["https://your-reference-image.png"],
        "model": "gpt-image-1",
        "size": "1536x1024",
        "quality": "hd",
        "n": 1
    }
    """
    
    if len(request.image_urls) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 reference images allowed")
    
    result = await service.generate_with_reference_urls(request)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ImageResponse(**result)