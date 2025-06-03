from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from ..models import ImageVariationRequest, ImageResponse, OpenAIModel, ImageSize, ImageFormat
from ..services.openai_service import OpenAIImageService

router = APIRouter()
service = OpenAIImageService()

@router.post("/variations", response_model=ImageResponse)
async def create_variations(
    image: UploadFile = File(..., description="Image file to create variations from"),
    model: OpenAIModel = Form(default=OpenAIModel.DALL_E_2, description="Model to use"),
    size: ImageSize = Form(default=ImageSize.SQUARE, description="Output size"),
    n: int = Form(default=1, description="Number of variations to generate"),
    response_format: ImageFormat = Form(default=ImageFormat.PNG, description="Output format"),
    save_to_disk: bool = Form(default=True, description="Save to disk")
):
    """
    Create variations of an existing image
    
    This endpoint:
    - Creates variations of the uploaded image
    - Only works with DALL-E 2 model
    - Does not require a text prompt
    - Generates similar but different versions of the input image
    
    Upload an image file to create variations from.
    """
    
    # Validate file type
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Only DALL-E 2 supports variations
    if model != OpenAIModel.DALL_E_2:
        raise HTTPException(status_code=400, detail="Variations are only supported with DALL-E 2 model")
    
    # Create request object
    request = ImageVariationRequest(
        model=model,
        size=size,
        n=n,
        response_format=response_format,
        save_to_disk=save_to_disk
    )
    
    result = await service.create_variations(request, image)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ImageResponse(**result)