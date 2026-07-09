from django.conf import settings
from .exceptions import RateLimitExceeded
from .redis_client import redis_client
import time
import uuid

#This class implements a fixed window rate limiting algorithm. It checks if a client has exceeded the allowed number of requests within a specified time window. 
#Its used by the middleware to determine whether to allow or block incoming requests based on the client's IP address.

class FixedWindowRateLimiter:

    def allow_request(self, key):

        limit = settings.RATE_LIMIT
        window = settings.RATE_LIMIT_WINDOW #static values taken from settings.py rather than hardcoding

        current_count = redis_client.get(key) # key will be of the form rate_limit+<client_ip>:number of requests made by that client in the current window          
        
        if current_count is None:
            redis_client.set(key, 1, ex=window)
            return True

        current_count=redis_client.incr(key) #Increment the count for the key in Redis (as value is in string format, Redis will convert it to int and increment it by 1 &  return the inc int)
        # Notice how we don't set the timeout again. The timeout is set only when the key is first created. 
        # This ensures that the window remains fixed.

        if current_count > limit:
            raise RateLimitExceeded(f"Rate limit exceeded.") #dont approve the request. The client has exceeded the rate limit for the current window.
    
class SlidingWindowRateLimiter:

    def allow_request(self, key):
        limit = settings.RATE_LIMIT
        window = settings.RATE_LIMIT_WINDOW
        current_time = int(time.time()) #time.time()-->returns something like 1752032530.3481, then we convert it into int  1752032530
        window_start = current_time - window # calculate window_start

        #Redis stores rate_limit<client_ip>:{member:score,member:score..}
        #member: a unique identifier
        #score: a timestamp representing when the request was made (used for sorting)
        #Now we delete every request older than window_start
        redis_client.zremrangebyscore(key, 0, window_start) # deletes everything outside (0,window_start)
        current_count = redis_client.zcard(key) #returns the size of sorted set

        if current_count >= limit:
            raise RateLimitExceeded("Rate limit exceeded. Please try again later." )
        
        #If the number of requests made by the client in the current window is less than the limit, allow the request and add it to the sorted set.
        request_id = str(uuid.uuid4()) #generate a unique id as member
        redis_client.zadd(key,{request_id: current_time}) #add in set

        redis_client.expire(key, window) #Imagine a client makes three request and disappear
        #but there data would stay in redis forever
        #so manually set the expiry

        
