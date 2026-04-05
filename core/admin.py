from django.contrib import admin
from .models import Cadastro, CampoFormulario, OpcaoCampo


@admin.register(Cadastro)
class CadastroAdmin(admin.ModelAdmin):
    list_display = (
        'id_ponto',
        'nome_cadastrador',
        'data_cadastro',
        'hora_cadastro',
        'latitude',
        'longitude',
        'status_sincronizacao',
    )
    search_fields = ('id_ponto', 'nome_cadastrador')
    list_filter = ('status_sincronizacao', 'data_cadastro')


@admin.register(CampoFormulario)
class CampoFormularioAdmin(admin.ModelAdmin):
    list_display = ('rotulo', 'nome_interno', 'tipo_campo')
    search_fields = ('rotulo', 'nome_interno')
    list_filter = ('tipo_campo',)


@admin.register(OpcaoCampo)
class OpcaoCampoAdmin(admin.ModelAdmin):
    list_display = ('campo', 'valor')
    search_fields = ('valor',)