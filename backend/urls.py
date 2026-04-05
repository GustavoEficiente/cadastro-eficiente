from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from core.api_views import (
    login_app,
    listar_campos,
    listar_cadastros,
    criar_cadastro,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/login/', login_app),
    path('api/campos/', listar_campos),
    path('api/cadastros/', listar_cadastros),
    path('api/cadastros/criar/', criar_cadastro),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)