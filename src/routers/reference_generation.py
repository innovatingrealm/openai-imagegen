from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import Optional, List
from ..models import ImageResponse, OpenAIModel, ImageSize, ImageFormat, ImageQuality
from ..services.openai_service import OpenAIImageService

router = APIRouter()
service = OpenAIImageService()

@router.post("/generate-with-reference", response_model=ImageResponse)
async def generate_with_reference_upload(
    reference_image: UploadFile = File(..., description="Reference image file"),
    prompt: str = Form(..., description="Generation prompt"),
    model: OpenAIModel = Form(default=OpenAIModel.GPT_IMAGE_1, description="Model to use (GPT-Image-1 recommended for references)"),
    size: ImageSize = Form(default=ImageSize.LANDSCAPE, description="Output size"),
    quality: ImageQuality = Form(default=ImageQuality.HIGH, description="Quality"),
    n: int = Form(default=1, description="Number of images to generate"),
    response_format: ImageFormat = Form(default=ImageFormat.PNG, description="Output format"),
    save_to_disk: bool = Form(default=True, description="Save to disk")
):
    """
    Generate a new image using an uploaded reference image with GPT-Image-1
    
    This endpoint:
    - Uses GPT-Image-1's advanced understanding of images
    - Takes an uploaded reference image for context
    - Generates new images based on the reference and prompt
    - Supports high-quality output with better instruction following
    
    Upload a reference image and provide a prompt for what you want to generate.
    """
    
    # Validate file type
    if not reference_image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Use GPT-Image-1's reference-based generation
    result = await service.generate_with_reference_gpt_image(
        reference_image, prompt, model, size, quality, n, response_format, save_to_disk
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ImageResponse(**result)

@router.post("/gpt-image-generate-with-url", response_model=ImageResponse)
async def gpt_image_generate_with_url(
    image_url: str = Form(..., description="Single reference image URL"),
    prompt: str = Form(..., description="Generation prompt"),
    size: ImageSize = Form(default=ImageSize.LANDSCAPE, description="Output size"),
    quality: ImageQuality = Form(default=ImageQuality.HIGH, description="Quality"),
    n: int = Form(default=1, description="Number of images to generate"),
    response_format: ImageFormat = Form(default=ImageFormat.PNG, description="Output format"),
    save_to_disk: bool = Form(default=True, description="Save to disk")
):
    """
    Generate image using GPT-Image-1 with a reference image URL
    
    This endpoint:
    - Takes a single image URL as reference
    - Uses GPT-Image-1 for generation
    - Downloads the image automatically
    - Perfect for n8n workflows with image URLs
    """
    
    # Use GPT-Image-1's URL-based generation
    result = await service.generate_with_reference_url_gpt_image(
        image_url, prompt, size, quality, n, response_format, save_to_disk
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ImageResponse(**result)

@router.post("/gpt-image-generate-with-multiple-urls", response_model=ImageResponse)
async def gpt_image_generate_with_multiple_urls(
    image_urls: List[str] = Form(..., description="Multiple reference image URLs (comma-separated or multiple form fields)"),
    prompt: str = Form(..., description="Generation prompt"),
    size: ImageSize = Form(default=ImageSize.LANDSCAPE, description="Output size"),
    quality: ImageQuality = Form(default=ImageQuality.HIGH, description="Quality"),
    n: int = Form(default=1, description="Number of images to generate"),
    response_format: ImageFormat = Form(default=ImageFormat.PNG, description="Output format"),
    save_to_disk: bool = Form(default=True, description="Save to disk")
):
    """
    Generate image using GPT-Image-1 with multiple reference image URLs
    
    This endpoint:
    - Takes multiple image URLs as references
    - Uses GPT-Image-1 for multi-reference generation
    - Downloads all images automatically
    - Perfect for complex n8n workflows
    """
    
    if len(image_urls) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 reference images allowed")
    
    # Use GPT-Image-1's multi-URL generation
    result = await service.generate_with_multiple_urls_gpt_image(
        image_urls, prompt, size, quality, n, response_format, save_to_disk
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ImageResponse(**result)

# JSON-based endpoints for easier n8n integration
@router.post("/gpt-image-generate-json", response_model=ImageResponse)
async def gpt_image_generate_json(request: dict):
    """
    Generate image using GPT-Image-1 with JSON input (supports URLs and multiple images)
    
    Example JSON:
    {
        "prompt": "Your generation prompt",
        "image_urls": ["url1", "url2", "url3"],
        "size": "1536x1024",
        "quality": "high",
        "n": 1,
        "save_to_disk": true
    }
    
    Perfect for n8n HTTP Request nodes with JSON body.
    """
    
    # Validate required fields
    if "prompt" not in request:
        raise HTTPException(status_code=400, detail="prompt is required")
    
    if "image_urls" not in request or not request["image_urls"]:
        raise HTTPException(status_code=400, detail="image_urls is required and must not be empty")
    
    # Extract parameters with defaults
    prompt = request["prompt"]
    image_urls = request["image_urls"]
    size = ImageSize(request.get("size", "1536x1024"))
    quality = ImageQuality(request.get("quality", "high"))
    n = request.get("n", 1)
    response_format = ImageFormat(request.get("response_format", "png"))
    save_to_disk = request.get("save_to_disk", True)
    
    if len(image_urls) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 reference images allowed")
    
    # Handle single vs multiple URLs
    if len(image_urls) == 1:
        result = await service.generate_with_reference_url_gpt_image(
            image_urls[0], prompt, size, quality, n, response_format, save_to_disk
        )
    else:
        result = await service.generate_with_multiple_urls_gpt_image(
            image_urls, prompt, size, quality, n, response_format, save_to_disk
        )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ImageResponse(**result)

@router.post("/gpt-image-generate-with-reference", response_model=ImageResponse)
async def gpt_image_generate_with_reference(
    reference_image: UploadFile = File(..., description="Reference image file"),
    prompt: str = Form(..., description="Generation prompt"),
    size: ImageSize = Form(default=ImageSize.LANDSCAPE, description="Output size"),
    quality: ImageQuality = Form(default=ImageQuality.HIGH, description="Quality"),
    n: int = Form(default=1, description="Number of images to generate"),
    response_format: ImageFormat = Form(default=ImageFormat.PNG, description="Output format"),
    save_to_disk: bool = Form(default=True, description="Save to disk")
):
    """
    Generate image using GPT-Image-1 with reference (Dedicated GPT-Image-1 endpoint)
    
    This endpoint ONLY uses GPT-Image-1 for reference-based generation.
    No model selection needed - always uses the most advanced model.
    """
    
    # Force GPT-Image-1
    model = OpenAIModel.GPT_IMAGE_1
    
    # Validate file type
    if not reference_image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Use GPT-Image-1's reference-based generation
    result = await service.generate_with_reference_gpt_image(
        reference_image, prompt, model, size, quality, n, response_format, save_to_disk
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ImageResponse(**result)

@router.post("/generate-with-multiple-references", response_model=ImageResponse)
async def generate_with_multiple_references(
    reference_images: List[UploadFile] = File(..., description="Multiple reference image files"),
    prompt: str = Form(..., description="Generation prompt"),
    model: OpenAIModel = Form(default=OpenAIModel.GPT_IMAGE_1, description="Model to use (GPT-Image-1 recommended for multi-references)"),
    size: ImageSize = Form(default=ImageSize.LANDSCAPE, description="Output size"),
    quality: ImageQuality = Form(default=ImageQuality.HIGH, description="Quality"),
    n: int = Form(default=1, description="Number of images to generate"),
    response_format: ImageFormat = Form(default=ImageFormat.PNG, description="Output format"),
    save_to_disk: bool = Form(default=True, description="Save to disk")
):
    """
    Generate a new image using multiple reference images with GPT-Image-1
    
    This endpoint:
    - Leverages GPT-Image-1's multi-image understanding
    - Takes multiple uploaded reference images
    - Synthesizes elements from all references with your prompt
    - Works best with 2-4 reference images
    
    Upload multiple reference images and provide a prompt for synthesis.
    """
    
    if len(reference_images) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 reference images allowed")
    
    # Validate file types
    for img in reference_images:
        if not img.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail=f"All files must be images. {img.filename} is not an image.")
    
    # Use GPT-Image-1's multi-reference generation
    result = await service.generate_with_multiple_references_gpt_image(
        reference_images, prompt, model, size, quality, n, response_format, save_to_disk
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ImageResponse(**result)