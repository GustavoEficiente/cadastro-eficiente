from django.contrib import admin
from django.utils.html import format_html
from .models import Cadastro, CampoFormulario, OpcaoCampo, FotoCadastro


class FotoCadastroInline(admin.TabularInline):
    model = FotoCadastro
    extra = 1
    max_num = 5
    fields = ("foto", "preview_foto", "criada_em")
    readonly_fields = ("preview_foto", "criada_em")

    def preview_foto(self, obj):
        if obj.pk and obj.foto:
            return format_html(
                '<img src="{}" style="max-height: 100px; border-radius: 8px; border: 1px solid #ccc;" />',
                obj.foto.url
            )
        return "Sem foto"

    preview_foto.short_description = "Pré-visualização"


@admin.register(Cadastro)
class CadastroAdmin(admin.ModelAdmin):
    list_display = (
        "id_ponto",
        "nome_cadastrador",
        "data_cadastro",
        "hora_cadastro",
        "latitude",
        "longitude",
        "status_sincronizacao",
        "total_fotos",
        "criado_em",
    )
    search_fields = (
        "id_ponto",
        "nome_cadastrador",
    )
    list_filter = (
        "status_sincronizacao",
        "data_cadastro",
        "criado_em",
    )
    readonly_fields = (
        "criado_em",
        "atualizado_em",
        "total_fotos",
    )
    inlines = [FotoCadastroInline]

    fieldsets = (
        ("Dados principais", {
            "fields": (
                "id_ponto",
                "nome_cadastrador",
                "data_cadastro",
                "hora_cadastro",
                "latitude",
                "longitude",
                "status_sincronizacao",
            )
        }),
        ("Dados extras do cadastro", {
            "fields": (
                "dados_extras",
            )
        }),
        ("Controle", {
            "fields": (
                "total_fotos",
                "criado_em",
                "atualizado_em",
            )
        }),
    )

    def total_fotos(self, obj):
        return obj.fotos.count()

    total_fotos.short_description = "Total de fotos"


@admin.register(CampoFormulario)
class CampoFormularioAdmin(admin.ModelAdmin):
    list_display = (
        "rotulo",
        "nome_interno",
        "tipo_campo",
        "obrigatorio",
        "ativo",
        "ordem",
        "usa_lista_opcoes",
        "placeholder",
    )
    search_fields = (
        "rotulo",
        "nome_interno",
    )
    list_filter = (
        "tipo_campo",
        "obrigatorio",
        "ativo",
        "usa_lista_opcoes",
    )
    ordering = (
        "ordem",
        "id",
    )


@admin.register(OpcaoCampo)
class OpcaoCampoAdmin(admin.ModelAdmin):
    list_display = (
        "campo",
        "valor",
        "ordem",
        "ativo",
    )
    search_fields = (
        "valor",
        "campo__rotulo",
        "campo__nome_interno",
    )
    list_filter = (
        "campo",
        "ativo",
    )
    ordering = (
        "campo",
        "ordem",
        "id",
    )


@admin.register(FotoCadastro)
class FotoCadastroAdmin(admin.ModelAdmin):
    list_display = (
        "cadastro",
        "preview_foto",
        "criada_em",
    )
    search_fields = (
        "cadastro__id_ponto",
        "cadastro__nome_cadastrador",
    )
    list_filter = (
        "criada_em",
    )
    readonly_fields = (
        "preview_foto",
        "criada_em",
    )

    def preview_foto(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="max-height: 120px; border-radius: 8px; border: 1px solid #ccc;" />',
                obj.foto.url
            )
        return "Sem foto"

    preview_foto.short_description = "Pré-visualização"