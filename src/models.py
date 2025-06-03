from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class ImageSize(str, Enum):
    SQUARE = "1024x1024"
    LANDSCAPE = "1536x1024"
    PORTRAIT = "1024x1536"

class ImageQuality(str, Enum):
    LOW = "low"
    STANDARD = "standard"
    HIGH = "high"  # For GPT-Image-1
    HD = "hd"      # For DALL-E 3

class ImageFormat(str, Enum):
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"

class OpenAIModel(str, Enum):
    DALL_E_2 = "dall-e-2"
    DALL_E_3 = "dall-e-3"
    GPT_IMAGE_1 = "gpt-image-1"

class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for image generation")
    model: OpenAIModel = Field(default=OpenAIModel.DALL_E_3, description="Model to use")
    size: ImageSize = Field(default=ImageSize.SQUARE, description="Image size")
    quality: ImageQuality = Field(default=ImageQuality.STANDARD, description="Image quality")
    n: int = Field(default=1, description="Number of images", ge=1, le=10)
    response_format: ImageFormat = Field(default=ImageFormat.PNG, description="Response format")
    save_to_disk: bool = Field(default=True, description="Save to disk")

class ReferenceGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for image generation")
    image_urls: List[str] = Field(..., description="Reference image URLs")
    model: OpenAIModel = Field(default=OpenAIModel.GPT_IMAGE_1, description="Model to use")
    size: ImageSize = Field(default=ImageSize.LANDSCAPE, description="Image size")
    quality: ImageQuality = Field(default=ImageQuality.HIGH, description="Image quality")
    n: int = Field(default=1, description="Number of images", ge=1, le=5)
    response_format: ImageFormat = Field(default=ImageFormat.PNG, description="Response format")
    save_to_disk: bool = Field(default=True, description="Save to disk")

class ImageResponse(BaseModel):
    success: bool
    message: str
    images: Optional[List[dict]] = None
    request_params: Optional[dict] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    openai_status: Optional[str] = None