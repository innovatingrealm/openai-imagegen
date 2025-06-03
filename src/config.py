import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Server Configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # API Configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50000000"))
    ALLOWED_IMAGE_FORMATS: List[str] = os.getenv("ALLOWED_IMAGE_FORMATS", "png,jpg,jpeg,webp").split(",")
    DEFAULT_IMAGE_SIZE: str = os.getenv("DEFAULT_IMAGE_SIZE", "1024x1024")
    DEFAULT_IMAGE_QUALITY: str = os.getenv("DEFAULT_IMAGE_QUALITY", "standard")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Directories
    GENERATED_IMAGES_DIR: str = "generated-images"
    LOGS_DIR: str = "logs"

# Create settings instance
settings = Settings()

# Validate required settings
if not settings.OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not set. Some features may not work.")

# Create directories if they don't exist
os.makedirs(settings.GENERATED_IMAGES_DIR, exist_ok=True)
os.makedirs(settings.LOGS_DIR, exist_ok=True)