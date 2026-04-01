from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from core.api_views import login_api, cidades_api, campos_api, cadastro_api


urlpatterns = [
    path('admin/', admin.site.urls),

    # Login do site
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Site
    path('', include('core.urls')),

    # API
    path('api/login/', login_api, name='api_login'),
    path('api/cidades/', cidades_api, name='api_cidades'),
    path('api/campos/', campos_api, name='api_campos'),
    path('api/cadastro/', cadastro_api, name='api_cadastro'),
]