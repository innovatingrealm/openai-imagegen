from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import Optional
from ..models import ImageEditRequest, ImageResponse, OpenAIModel, ImageSize, ImageFormat
from ..services.openai_service import OpenAIImageService

router = APIRouter()
service = OpenAIImageService()

@router.post("/edit", response_model=ImageResponse)
async def edit_image(
    image: UploadFile = File(..., description="Image file to edit"),
    mask: Optional[UploadFile] = File(None, description="Mask file for inpainting (optional)"),
    prompt: str = Form(..., description="Edit prompt"),
    model: OpenAIModel = Form(default=OpenAIModel.DALL_E_2, description="Model to use"),
    size: ImageSize = Form(default=ImageSize.SQUARE, description="Output size"),
    n: int = Form(default=1, description="Number of images to generate"),
    response_format: ImageFormat = Form(default=ImageFormat.PNG, description="Output format"),
    save_to_disk: bool = Form(default=True, description="Save to disk")
):
    """
    Edit an existing image with a text prompt
    
    This endpoint supports:
    - Image editing with text prompts
    - Optional mask for inpainting (editing specific areas)
    - Multiple models (DALL-E 2, GPT-Image-1)
    - Various output sizes and formats
    
    Upload the image file and optionally a mask file for inpainting.
    The mask should be a PNG with transparent areas indicating where to edit.
    """
    
    # Validate file types
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    if mask and not mask.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Mask file must be an image")
    
    # Create request object
    request = ImageEditRequest(
        prompt=prompt,
        model=model,
        size=size,
        n=n,
        response_format=response_format,
        save_to_disk=save_to_disk
    )
    
    result = await service.edit_image(request, image, mask)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ImageResponse(**result)