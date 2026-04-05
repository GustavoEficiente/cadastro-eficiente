from django.contrib import admin
from django.utils.html import format_html
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
        'tem_fotos',
    )
    search_fields = ('id_ponto', 'nome_cadastrador')
    list_filter = ('status_sincronizacao', 'data_cadastro')
    readonly_fields = (
        'preview_foto_1',
        'preview_foto_2',
        'preview_foto_3',
        'preview_foto_4',
        'preview_foto_5',
        'criado_em',
        'atualizado_em',
    )

    fieldsets = (
        ('Dados principais', {
            'fields': (
                'id_ponto',
                'nome_cadastrador',
                'usuario',
                'data_cadastro',
                'hora_cadastro',
                'latitude',
                'longitude',
                'status_sincronizacao',
                'dados_extras',
            )
        }),
        ('Fotos', {
            'fields': (
                'foto_1', 'preview_foto_1',
                'foto_2', 'preview_foto_2',
                'foto_3', 'preview_foto_3',
                'foto_4', 'preview_foto_4',
                'foto_5', 'preview_foto_5',
            )
        }),
        ('Controle', {
            'fields': ('criado_em', 'atualizado_em')
        })
    )

    def _preview(self, obj, campo):
        arquivo = getattr(obj, campo)
        if arquivo:
            return format_html('<a href="{}" target="_blank"><img src="{}" width="120" style="border-radius:8px;border:1px solid #ccc;" /></a>', arquivo.url, arquivo.url)
        return 'Sem foto'

    def preview_foto_1(self, obj):
        return self._preview(obj, 'foto_1')

    def preview_foto_2(self, obj):
        return self._preview(obj, 'foto_2')

    def preview_foto_3(self, obj):
        return self._preview(obj, 'foto_3')

    def preview_foto_4(self, obj):
        return self._preview(obj, 'foto_4')

    def preview_foto_5(self, obj):
        return self._preview(obj, 'foto_5')

    def tem_fotos(self, obj):
        return any([obj.foto_1, obj.foto_2, obj.foto_3, obj.foto_4, obj.foto_5])

    tem_fotos.boolean = True
    preview_foto_1.short_description = 'Prévia foto 1'
    preview_foto_2.short_description = 'Prévia foto 2'
    preview_foto_3.short_description = 'Prévia foto 3'
    preview_foto_4.short_description = 'Prévia foto 4'
    preview_foto_5.short_description = 'Prévia foto 5'


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