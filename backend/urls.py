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
    # CADASTRO (ROTA CORRETA)
    # =========================
    path('api/cadastros/criar/', criar_cadastro),

    # =========================
    # 🔥 ROTAS ALTERNATIVAS (COMPATIBILIDADE COM APP)
    # =========================
    path('api/cadastro/', criar_cadastro),
    path('api/cadastros', criar_cadastro),      # sem barra
    path('api/sincronizar/', criar_cadastro),
    path('api/sincronizar', criar_cadastro),
]

# =========================
# MEDIA (FOTOS)
# =========================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)