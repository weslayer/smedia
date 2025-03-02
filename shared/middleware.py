from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Callable
import time
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)

# Rate limiting configuration
RATE_LIMIT_DURATION = 60  # seconds
MAX_REQUESTS = 100  # requests per duration
SENSITIVE_ENDPOINTS = {
    "/users/login": 5,  # 5 attempts per minute
    "/users/": 10,      # 10 new accounts per minute
}

# Store for rate limiting
rate_limit_store = defaultdict(lambda: {"count": 0, "reset_time": 0})
rate_limit_lock = asyncio.Lock()

async def rate_limit_middleware(request: Request, call_next: Callable):
    client_ip = request.client.host
    path = request.url.path
    current_time = time.time()

    # Get rate limit for this endpoint
    max_requests = SENSITIVE_ENDPOINTS.get(path, MAX_REQUESTS)
    
    async with rate_limit_lock:
        # Reset counter if duration has passed
        if current_time > rate_limit_store[client_ip]["reset_time"]:
            rate_limit_store[client_ip] = {
                "count": 0,
                "reset_time": current_time + RATE_LIMIT_DURATION
            }
        
        # Increment counter
        rate_limit_store[client_ip]["count"] += 1
        
        # Check if limit exceeded
        if rate_limit_store[client_ip]["count"] > max_requests:
            reset_time = rate_limit_store[client_ip]["reset_time"] - current_time
            raise HTTPException(
                status_code=429,
                detail={
                    "message": "Too many requests",
                    "retry_after": int(reset_time)
                }
            )

    # Error handling middleware
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

async def error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"}) 