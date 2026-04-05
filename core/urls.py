from django.urls import path
from .views import listar_campos, listar_cadastros, sincronizar_cadastro

urlpatterns = [
    path('campos/', listar_campos, name='listar_campos'),
    path('cadastros/', listar_cadastros, name='listar_cadastros'),
    path('sincronizar/', sincronizar_cadastro, name='sincronizar_cadastro'),
]