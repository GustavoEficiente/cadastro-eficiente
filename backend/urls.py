from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from core.api_views import (
    login_api,
    campos_api,
    cadastros_api,
    cadastro_completo_api,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path("", include("core.urls")),

    path("api/login/", login_api, name="login_api"),
    path("api/campos/", campos_api, name="campos_api"),
    path("api/cadastros/", cadastros_api, name="cadastros_api"),
    path("api/cadastro-completo/", cadastro_completo_api, name="cadastro_completo_api"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)