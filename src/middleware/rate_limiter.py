from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict, deque
from typing import Dict
from ..config import settings

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.limit = settings.RATE_LIMIT_PER_MINUTE
        self.window = 60  # 60 seconds
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path == "/health":
            response = await call_next(request)
            return response
        
        # Get client IP
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old requests
        while self.requests[client_ip] and self.requests[client_ip][0] < current_time - self.window:
            self.requests[client_ip].popleft()
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.limit:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.limit} requests per minute allowed",
                    "retry_after": int(self.window - (current_time - self.requests[client_ip][0]))
                }
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        return response