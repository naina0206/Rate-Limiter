from django.urls import path
from .views import apiLogic

urlpatterns = [
    path("public_api/", apiLogic),
]