from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request


from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler

from fastapi.responses import JSONResponse



limiter = Limiter(key_func=get_remote_address)

def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests"
        }
    )