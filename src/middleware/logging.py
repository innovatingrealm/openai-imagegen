from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import json
from datetime import datetime
from ..config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{settings.LOGS_DIR}/api.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("openai_image_api")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "client_ip": request.client.host
        }
        
        if response.status_code >= 400:
            logger.error(f"Error response: {json.dumps(log_data)}")
        else:
            logger.info(f"Response: {json.dumps(log_data)}")
        
        # Add processing time to response headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response