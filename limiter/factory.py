from django.conf import settings

from .services import (
    FixedWindowRateLimiter,
    SlidingWindowRateLimiter,
)

def get_rate_limiter():

    algorithm = settings.RATE_LIMIT_ALGORITHM

    if algorithm == "fixed":
        return FixedWindowRateLimiter()
    
    if algorithm == "sliding":
        return SlidingWindowRateLimiter()

    raise ValueError(f"Unsupported algorithm: {algorithm}")