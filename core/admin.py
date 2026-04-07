import json
from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponse
from django.urls import path
from django.utils.dateparse import parse_date
from django.utils.html import format_html

import pandas as pd

from .models import Cadastro


def obter_cidade(cadastro):
    dados = cadastro.dados_extras or {}
    if not isinstance(dados, dict):
        return ''

    chaves_possiveis = [
        'cidade',
        'municipio',
        'município',
        'city',
        'localidade',
    ]

    for chave in chaves_possiveis:
        valor = dados.get(chave)
        if valor:
            return str(valor)

    return ''


def obter_foto_nome(cadastro):
    try:
        if cadastro.foto:
            return cadastro.foto.name
    except Exception:
        pass
    return ''


def obter_foto_url_absoluta(cadastro):
    try:
        if cadastro.foto:
            url = cadastro.foto.url
            if url.startswith('http://') or url.startswith('https://'):
                return url
            return f"https://cadastro-eficiente-1.onrender.com{url}"
    except Exception:
        pass
    return ''


def obter_todas_as_chaves_dados_extras(queryset):
    chaves = set()

    for cadastro in queryset:
        dados = cadastro.dados_extras or {}
        if isinstance(dados, dict):
            for chave in dados.keys():
                chaves.add(str(chave))

    return sorted(chaves)


def obter_linhas_exportacao(queryset):
    chaves_extras = obter_todas_as_chaves_dados_extras(queryset)
    linhas = []

    for cadastro in queryset:
        dados = cadastro.dados_extras or {}

        linha = {
            'id_ponto': cadastro.id_ponto,
            'nome_cadastrador': cadastro.nome_cadastrador,
            'data_cadastro': cadastro.data_cadastro.strftime('%d/%m/%Y') if cadastro.data_cadastro else '',
            'hora_cadastro': cadastro.hora_cadastro.strftime('%H:%M:%S') if cadastro.hora_cadastro else '',
            'latitude': cadastro.latitude,
            'longitude': cadastro.longitude,
            'cidade': obter_cidade(cadastro),
            'status_sincronizacao': cadastro.status_sincronizacao,
            'foto_nome': obter_foto_nome(cadastro),
            'foto_url': obter_foto_url_absoluta(cadastro),
        }

        for chave in chaves_extras:
            linha[chave] = dados.get(chave, '') if isinstance(dados, dict) else ''

        linhas.append(linha)

    return linhas, chaves_extras


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
    search_fields = ('id_ponto', 'nome_cadastrador')
    list_filter = ('status_sincronizacao', 'data_cadastro')
    change_list_template = 'admin/core/cadastro/change_list.html'

    readonly_fields = ('foto_link_admin', 'foto_preview')

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
                '<a href="{0}" target="_blank">'
                '<img src="{0}" style="max-height:300px; border:1px solid #ccc; border-radius:8px;" />'
                '</a>',
                obj.foto.url
            )
        return 'Sem preview'
    foto_preview.short_description = 'Preview da foto'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'exportar-relatorio/',
                self.admin_site.admin_view(self.exportar_relatorio_view),
                name='core_cadastro_exportar_relatorio',
            ),
        ]
        return custom_urls + urls

    def exportar_relatorio_view(self, request):
        nome_cadastrador = (request.GET.get('nome_cadastrador') or '').strip()
        cidade = (request.GET.get('cidade') or '').strip()
        data_inicial = request.GET.get('data_inicial') or ''
        data_final = request.GET.get('data_final') or ''
        formato = (request.GET.get('formato') or '').strip().lower()

        queryset = Cadastro.objects.all().order_by('-data_cadastro', '-hora_cadastro', '-id')

        if nome_cadastrador:
            queryset = queryset.filter(nome_cadastrador__icontains=nome_cadastrador)

        data_inicial_parse = parse_date(data_inicial) if data_inicial else None
        data_final_parse = parse_date(data_final) if data_final else None

        if data_inicial_parse:
            queryset = queryset.filter(data_cadastro__gte=data_inicial_parse)

        if data_final_parse:
            queryset = queryset.filter(data_cadastro__lte=data_final_parse)

        if cidade:
            ids_filtrados = []
            for cadastro in queryset:
                cidade_cadastro = obter_cidade(cadastro)
                if cidade.lower() in cidade_cadastro.lower():
                    ids_filtrados.append(cadastro.id)
            queryset = queryset.filter(id__in=ids_filtrados)

        if not queryset.exists():
            self.message_user(
                request,
                'Nenhum cadastro encontrado com os filtros informados.',
                level=messages.WARNING,
            )
            return HttpResponse('Nenhum cadastro encontrado.', status=404)

        linhas, _ = obter_linhas_exportacao(queryset)

        if formato == 'csv':
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename="cadastros.csv"'
            df = pd.DataFrame(linhas)
            response.write(df.to_csv(index=False))
            return response

        if formato == 'excel':
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="cadastros.xlsx"'
            df = pd.DataFrame(linhas)
            with pd.ExcelWriter(response, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Cadastros')
            return response

        return HttpResponse('Formato inválido.', status=400)