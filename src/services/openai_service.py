import base64
import os
import requests
from datetime import datetime
from typing import List
from io import BytesIO
from PIL import Image
import openai
from ..config import settings
from ..models import ImageGenerationRequest, ReferenceGenerationRequest

class OpenAIImageService:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
    
    async def generate_image(self, request: ImageGenerationRequest) -> dict:
        """Generate image from text prompt"""
        try:
            if not self.client:
                return {
                    "success": False,
                    "error": "OpenAI API key not configured",
                    "message": "Please set OPENAI_API_KEY environment variable"
                }
            
            response = self.client.images.generate(
                model=request.model.value,
                prompt=request.prompt,
                size=request.size.value,
                quality=request.quality.value,
                n=request.n,
                response_format="b64_json"
            )
            
            images = []
            for idx, image_data in enumerate(response.data):
                image_info = {
                    "index": idx,
                    "b64_json": image_data.b64_json,
                    "revised_prompt": getattr(image_data, 'revised_prompt', None)
                }
                
                if request.save_to_disk:
                    filename = await self._save_image_to_disk(
                        image_data.b64_json, 
                        f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx}",
                        request.response_format.value
                    )
                    image_info["filename"] = filename
                    image_info["file_path"] = f"{settings.GENERATED_IMAGES_DIR}/{filename}"
                
                images.append(image_info)
            
            return {
                "success": True,
                "message": f"Successfully generated {len(images)} image(s)",
                "images": images,
                "request_params": {
                    "model": request.model.value,
                    "prompt": request.prompt,
                    "size": request.size.value,
                    "quality": request.quality.value,
                    "n": request.n
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate image"
            }
    
    async def generate_with_reference_urls(self, request: ReferenceGenerationRequest) -> dict:
        """Generate image using reference URLs with GPT-Image-1"""
        try:
            if not self.client:
                return {
                    "success": False,
                    "error": "OpenAI API key not configured",
                    "message": "Please set OPENAI_API_KEY environment variable"
                }
            
            if not request.image_urls:
                return {
                    "success": False,
                    "error": "No reference images provided",
                    "message": "Please provide at least one reference image URL"
                }
            
            # Download and process the first reference image
            raw_data, processed_image_file = await self._download_image_from_url(request.image_urls[0])
            
            # Create enhanced prompt
            enhanced_prompt = self._create_enhanced_prompt(request.prompt, len(request.image_urls))
            
            # Use the simpler approach: save to temp file and use file path
            temp_filename = f"temp_ref_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            temp_path = os.path.join(settings.GENERATED_IMAGES_DIR, temp_filename)
            
            # Write processed image to temp file
            with open(temp_path, 'wb') as f:
                processed_image_file.seek(0)
                f.write(processed_image_file.read())
            
            try:
                # Use GPT-Image-1's edit endpoint with file
                with open(temp_path, 'rb') as image_file:
                    response = self.client.images.edit(
                        model=request.model.value,
                        image=image_file,
                        prompt=enhanced_prompt,
                        size=request.size.value,
                        n=request.n
                    )
            finally:
                # Clean up temp file
                try:
                    os.remove(temp_path)
                except:
                    pass
            
            images = []
            for idx, image_data_response in enumerate(response.data):
                # The edit endpoint typically returns URLs, not base64
                if hasattr(image_data_response, 'url') and image_data_response.url:
                    # Download the image from URL and convert to base64
                    img_response = requests.get(image_data_response.url)
                    img_response.raise_for_status()
                    b64_data = base64.b64encode(img_response.content).decode('utf-8')
                elif hasattr(image_data_response, 'b64_json') and image_data_response.b64_json:
                    b64_data = image_data_response.b64_json
                else:
                    continue
                
                image_info = {
                    "index": idx,
                    "b64_json": b64_data
                }
                
                if request.save_to_disk:
                    filename = await self._save_image_to_disk(
                        b64_data, 
                        f"reference_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx}",
                        request.response_format.value
                    )
                    image_info["filename"] = filename
                    image_info["file_path"] = f"{settings.GENERATED_IMAGES_DIR}/{filename}"
                
                images.append(image_info)
            
            return {
                "success": True,
                "message": f"Successfully generated {len(images)} image(s) using {len(request.image_urls)} reference(s)",
                "images": images,
                "request_params": {
                    "model": request.model.value,
                    "original_prompt": request.prompt,
                    "enhanced_prompt": enhanced_prompt,
                    "size": request.size.value,
                    "n": request.n,
                    "reference_count": len(request.image_urls),
                    "reference_urls": request.image_urls,
                    "note": "Quality parameter not supported by edit endpoint"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate image with references"
            }
    
    def _create_enhanced_prompt(self, original_prompt: str, ref_count: int) -> str:
        """Create enhanced prompt incorporating reference information"""
        if ref_count == 1:
            return f"Create a new image based on this reference: {original_prompt}. Use the style, composition, and visual elements from the reference image as inspiration while generating the requested scene."
        else:
            return f"Create a new image combining elements from {ref_count} reference images: {original_prompt}. Synthesize the visual styles, color palettes, and artistic elements from all references into a cohesive artwork."
    
    async def _process_image_for_openai(self, image_data: bytes) -> BytesIO:
        """Process image data to ensure it's in a format OpenAI accepts"""
        try:
            # Open the image with PIL to ensure it's valid
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if necessary (removes alpha channel)
            if image.mode in ('RGBA', 'LA'):
                # Create a white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                else:
                    background.paste(image)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save as PNG (most reliable format for OpenAI)
            processed_image = BytesIO()
            image.save(processed_image, format='PNG', quality=95)
            processed_image.seek(0)
            
            return processed_image
            
        except Exception as e:
            raise ValueError(f"Invalid image data: {str(e)}")
    
    async def _download_image_from_url(self, url: str) -> tuple:
        """Download image from URL and return both raw bytes and processed file"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(url, timeout=30, headers=headers, stream=True)
        response.raise_for_status()
        
        # Get the raw image data
        raw_data = response.content
        
        # Process the image to ensure it's in the right format
        processed_image = await self._process_image_for_openai(raw_data)
        
        return raw_data, processed_image
    
    async def _save_image_to_disk(self, b64_json: str, filename_prefix: str, format: str) -> str:
        """Save base64 image to disk"""
        image_data = base64.b64decode(b64_json)
        filename = f"{filename_prefix}.{format}"
        filepath = os.path.join(settings.GENERATED_IMAGES_DIR, filename)
        
        with open(filepath, "wb") as f:
            f.write(image_data)
        
        return filename
    
    async def check_api_status(self) -> bool:
        """Check if OpenAI API is accessible"""
        try:
            if not self.client:
                return False
            self.client.models.list()
            return True
        except Exception:
            return False