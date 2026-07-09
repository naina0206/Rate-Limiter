def get_client_ip(request):
    """
    To get client's IP
    """

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR") 
    # request.META=Dict of HTTP request metadata 

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip() 
    # return HTTP_X_FORWARDED_FOR if a load balancer like Nginx is present 
    # because REMOTE_ADDR would be of load balancer rather than client
    # It makes production ready code

    return request.META.get("REMOTE_ADDR") # for local testing, REMOTE_ADDR would be of client itself, so return it   

def generate_rate_limit_key(ip):
    """
    Creates a Redis key for storing request counts.
    """
    return f"rate_limit:{ip}"                              
    # If the client IP is 127.0.0.1 the Redis key becomes rate_limit:127.0.0.1  
    # Later, Redis might contain:-- Key:rate_limit:127.0.0.1, Value:18, TTL:43 seconds                              