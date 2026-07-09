from rest_framework import status
from django.http import JsonResponse
from .factory import get_rate_limiter
from .exceptions import RateLimitExceeded

from .utils import get_client_ip, generate_rate_limit_key


class RateLimiterMiddleware:

    def __init__(self, get_response):
        #when django starts it creates the middleware object once
        #it happens only once when django starts not for every request
        #so init is called once
        self.get_response = get_response #django makes a pipeline of middleware
        #like session middleware -> Authentication middleware -> ... and then executes them line by line,
        #so to execute next middleware the current middleware has to pass it control
        #get_response(request) method does that
        #get_response->It represents the next step in the request-processing chain
        #so when i execute init I will add get_response as instance attribute (self.get_response) so that __call__ will have access to it
        self.limiter = get_rate_limiter() #make an object once and add this to self (instance variable)
        # if using a different algorithm, we can change the factory to return a different object based on settings.py
        # for eg- get_rate_limiter() return FixedWindowRateLimiter() object, which is then called by middleware

    def __call__(self, request):
        # executes for every request
        #any object having __call__ can be called like a function.
        # django makes an object middleware=ratelimitingmiddleware(request)
        # then it called middleware() --> which would translate to middleware.__call__()

        client_ip = get_client_ip(request) #get the client ip

        key = generate_rate_limit_key(client_ip) #generate redis key for the client ip
        #see how middleware never checks count, aor block ips.
        try:
            self.limiter.allow_request(key)

        except RateLimitExceeded as e:
            return JsonResponse(
                {"error": str(e)},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        return self.get_response(request) #pass control to next middleware