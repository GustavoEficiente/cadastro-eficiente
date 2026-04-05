from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.dateparse import parse_date

from openpyxl import Workbook
import csv
import simplekml

from .models import Cadastro, CampoFormulario, OpcaoCampo


def obter_cidade(cadastro):
    dados = cadastro.dados_extras or {}

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


def obter_foto_url(cadastro):
    try:
        if cadastro.foto:
            return cadastro.foto.url
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
            'foto_url': obter_foto_url(cadastro),
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
    )
    search_fields = ('id_ponto', 'nome_cadastrador')
    list_filter = ('status_sincronizacao', 'data_cadastro')
    change_list_template = 'admin/core/cadastro/change_list.html'

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

        if formato:
            if not queryset.exists():
                self.message_user(
                    request,
                    'Nenhum cadastro encontrado com os filtros informados.',
                    level=messages.WARNING
                )
                return render(
                    request,
                    'admin/core/exportar_relatorio.html',
                    {
                        **self.admin_site.each_context(request),
                        'title': 'Exportar relatório de cadastros',
                        'filtros': {
                            'nome_cadastrador': nome_cadastrador,
                            'cidade': cidade,
                            'data_inicial': data_inicial,
                            'data_final': data_final,
                        }
                    }
                )

            if formato == 'csv':
                return self.exportar_csv(queryset)

            if formato == 'excel':
                return self.exportar_excel(queryset)

            if formato == 'kml':
                return self.exportar_kml(queryset)

        return render(
            request,
            'admin/core/exportar_relatorio.html',
            {
                **self.admin_site.each_context(request),
                'title': 'Exportar relatório de cadastros',
                'filtros': {
                    'nome_cadastrador': nome_cadastrador,
                    'cidade': cidade,
                    'data_inicial': data_inicial,
                    'data_final': data_final,
                }
            }
        )

    def exportar_csv(self, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="cadastros_filtrados.csv"'

        response.write('\ufeff')
        writer = csv.writer(response, delimiter=';')

        linhas, chaves_extras = obter_linhas_exportacao(queryset)

        cabecalho = [
            'ID Ponto',
            'Nome Cadastrador',
            'Data Cadastro',
            'Hora Cadastro',
            'Latitude',
            'Longitude',
            'Cidade',
            'Status Sincronização',
        ]
        cabecalho.extend(chaves_extras)
        cabecalho.extend(['Foto Nome', 'Foto URL'])

        writer.writerow(cabecalho)

        for linha in linhas:
            row = [
                linha['id_ponto'],
                linha['nome_cadastrador'],
                linha['data_cadastro'],
                linha['hora_cadastro'],
                linha['latitude'],
                linha['longitude'],
                linha['cidade'],
                linha['status_sincronizacao'],
            ]

            for chave in chaves_extras:
                row.append(linha.get(chave, ''))

            row.extend([
                linha['foto_nome'],
                linha['foto_url'],
            ])

            writer.writerow(row)

        return response

    def exportar_excel(self, queryset):
        wb = Workbook()
        ws = wb.active
        ws.title = 'Cadastros'

        linhas, chaves_extras = obter_linhas_exportacao(queryset)

        cabecalho = [
            'ID Ponto',
            'Nome Cadastrador',
            'Data Cadastro',
            'Hora Cadastro',
            'Latitude',
            'Longitude',
            'Cidade',
            'Status Sincronização',
        ]
        cabecalho.extend(chaves_extras)
        cabecalho.extend(['Foto Nome', 'Foto URL'])

        ws.append(cabecalho)

        for linha in linhas:
            row = [
                linha['id_ponto'],
                linha['nome_cadastrador'],
                linha['data_cadastro'],
                linha['hora_cadastro'],
                linha['latitude'],
                linha['longitude'],
                linha['cidade'],
                linha['status_sincronizacao'],
            ]

            for chave in chaves_extras:
                row.append(linha.get(chave, ''))

            row.extend([
                linha['foto_nome'],
                linha['foto_url'],
            ])

            ws.append(row)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="cadastros_filtrados.xlsx"'
        wb.save(response)
        return response

    def exportar_kml(self, queryset):
        kml = simplekml.Kml()

        linhas, chaves_extras = obter_linhas_exportacao(queryset)

        for linha in linhas:
            if linha['longitude'] in [None, ''] or linha['latitude'] in [None, '']:
                continue

            descricao = (
                f"ID Ponto: {linha['id_ponto']}\n"
                f"Cadastrador: {linha['nome_cadastrador']}\n"
                f"Data: {linha['data_cadastro']}\n"
                f"Hora: {linha['hora_cadastro']}\n"
                f"Cidade: {linha['cidade']}\n"
                f"Status: {linha['status_sincronizacao']}\n"
            )

            for chave in chaves_extras:
                descricao += f"{chave}: {linha.get(chave, '')}\n"

            descricao += f"Foto Nome: {linha['foto_nome']}\n"
            descricao += f"Foto URL: {linha['foto_url']}\n"

            kml.newpoint(
                name=linha['id_ponto'],
                coords=[(float(linha['longitude']), float(linha['latitude']))],
                description=descricao,
            )

        response = HttpResponse(content_type='application/vnd.google-earth.kml+xml')
        response['Content-Disposition'] = 'attachment; filename="cadastros_filtrados.kml"'
        response.write(kml.kml())
        return response


@admin.register(CampoFormulario)
class CampoFormularioAdmin(admin.ModelAdmin):
    list_display = ('rotulo', 'nome_interno', 'tipo_campo')
    search_fields = ('rotulo', 'nome_interno')
    list_filter = ('tipo_campo',)


@admin.register(OpcaoCampo)
class OpcaoCampoAdmin(admin.ModelAdmin):
    list_display = ('campo', 'valor')
    search_fields = ('valor',)