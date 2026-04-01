from django.contrib import admin
from .models import Cidade, Cadastro, CampoFormulario, OpcaoCampo


@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'uf', 'ativo')
    list_filter = ('uf', 'ativo')
    search_fields = ('nome', 'uf')


@admin.register(Cadastro)
class CadastroAdmin(admin.ModelAdmin):
    list_display = (
        'id_ponto',
        'cidade',
        'nome_cadastrador',
        'usuario',
        'data_cadastro',
        'hora_cadastro',
        'tipo_coordenada',
        'latitude',
        'longitude',
        'status_sincronizacao',
    )
    search_fields = ('id_ponto', 'nome_cadastrador', 'cidade__nome', 'usuario__username')
    list_filter = (
        'cidade',
        'usuario',
        'tipo_coordenada',
        'status_sincronizacao',
        'data_cadastro',
    )


@admin.register(CampoFormulario)
class CampoFormularioAdmin(admin.ModelAdmin):
    list_display = (
        'rotulo',
        'nome_interno',
        'tipo_campo',
        'obrigatorio',
        'ativo',
        'ordem',
        'usa_lista_opcoes',
    )
    list_filter = ('tipo_campo', 'ativo', 'obrigatorio')
    search_fields = ('rotulo', 'nome_interno')
    ordering = ('ordem',)


@admin.register(OpcaoCampo)
class OpcaoCampoAdmin(admin.ModelAdmin):
    list_display = ('campo', 'valor', 'ordem', 'ativo')
    list_filter = ('campo', 'ativo')
    search_fields = ('valor',)
    ordering = ('campo', 'ordem')