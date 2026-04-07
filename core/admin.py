from django.contrib import admin
from django.utils.html import format_html

from .models import Cadastro


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
        'foto_link',
    )

    search_fields = (
        'id_ponto',
        'nome_cadastrador',
    )

    list_filter = (
        'status_sincronizacao',
        'data_cadastro',
    )

    readonly_fields = (
        'foto_link_admin',
        'foto_preview',
    )

    fields = (
        'id_ponto',
        'nome_cadastrador',
        'data_cadastro',
        'hora_cadastro',
        'latitude',
        'longitude',
        'foto',
        'foto_link_admin',
        'foto_preview',
        'status_sincronizacao',
        'dados_extras',
    )

    def foto_link(self, obj):
        if obj and obj.foto:
            return format_html('<a href="{}" target="_blank">Abrir foto</a>', obj.foto.url)
        return 'Sem foto'
    foto_link.short_description = 'Link da foto'

    def foto_link_admin(self, obj):
        if obj and obj.foto:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.foto.url, obj.foto.name)
        return 'Sem foto'
    foto_link_admin.short_description = 'Link da foto'

    def foto_preview(self, obj):
        if obj and obj.foto:
            return format_html(
                '<img src="{}" style="max-height:300px; border:1px solid #ccc; border-radius:8px;" />',
                obj.foto.url
            )
        return 'Sem preview'
    foto_preview.short_description = 'Preview da foto'