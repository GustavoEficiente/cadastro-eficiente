from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from core.api_views import (
    login_app,
    listar_campos,
    listar_cadastros,
    criar_cadastro,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # =========================
    # LOGIN
    # =========================
    path('api/login/', login_app),

    # =========================
    # CAMPOS DO FORMULÁRIO
    # =========================
    path('api/campos/', listar_campos),

    # =========================
    # LISTAGEM
    # =========================
    path('api/cadastros/', listar_cadastros),

    # =========================
    # CADASTRO
    # =========================
    path('api/cadastros/criar/', criar_cadastro),

    # =========================
    # ROTAS EXTRA (APP)
    # =========================
    path('api/cadastro/', criar_cadastro),
    path('api/cadastros', criar_cadastro),
    path('api/sincronizar/', criar_cadastro),
    path('api/sincronizar', criar_cadastro),
]

# 🔥 LOCAL (já tinha)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 🔥 PRODUÇÃO (ESSA É A CORREÇÃO)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]