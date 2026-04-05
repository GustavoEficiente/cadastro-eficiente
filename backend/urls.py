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

    path('api/login/', login_app, name='api_login'),
    path('api/campos/', listar_campos, name='api_campos'),
    path('api/cadastros/', listar_cadastros, name='api_cadastros'),
    path('api/cadastros/criar/', criar_cadastro, name='api_cadastros_criar'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)