from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(["GET"])
def apiLogic(request):
    return Response({"message": "Successful response from public API"}, status=200)