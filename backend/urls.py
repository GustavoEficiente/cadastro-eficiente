from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("API Cadastro Eficiente está online 🚀")

urlpatterns = [
    path('', home),  # 👈 ISSO AQUI RESOLVE O NOT FOUND
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
]