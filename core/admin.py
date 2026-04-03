from django.contrib import admin
from .models import Cadastro, CampoFormulario, OpcaoCampo, FotoCadastro


class FotoCadastroInline(admin.TabularInline):
    model = FotoCadastro
    extra = 0


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
        "criado_em",
    )
    search_fields = ("id_ponto", "nome_cadastrador")
    list_filter = ("status_sincronizacao", "data_cadastro")
    inlines = [FotoCadastroInline]


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
    )
    search_fields = ("rotulo", "nome_interno")
    list_filter = ("tipo_campo", "ativo", "obrigatorio")
    ordering = ("ordem", "id")


@admin.register(OpcaoCampo)
class OpcaoCampoAdmin(admin.ModelAdmin):
    list_display = ("campo", "valor", "ordem", "ativo")
    search_fields = ("valor",)
    list_filter = ("campo", "ativo")
    ordering = ("campo", "ordem", "id")


@admin.register(FotoCadastro)
class FotoCadastroAdmin(admin.ModelAdmin):
    list_display = ("cadastro", "foto", "criada_em")