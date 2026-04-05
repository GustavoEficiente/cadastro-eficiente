from django.urls import path
from .views import api_login, api_campos, api_cadastro, api_cadastros

urlpatterns = [
    path('login/', api_login),
    path('campos/', api_campos),
    path('cadastro/', api_cadastro),
    path('cadastros/', api_cadastros),
]