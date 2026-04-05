from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.dateparse import parse_date

from openpyxl import Workbook
import csv
import json
import simplekml

from .models import Cadastro, CampoFormulario, OpcaoCampo


def obter_cidade(cadastro):
    """
    Tenta achar a cidade dentro de dados_extras.
    Ajustei para aceitar vários nomes comuns.
    """
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


def obter_linhas_exportacao(queryset):
    linhas = []

    for cadastro in queryset:
        linhas.append({
            'id_ponto': cadastro.id_ponto,
            'nome_cadastrador': cadastro.nome_cadastrador,
            'data_cadastro': cadastro.data_cadastro.strftime('%d/%m/%Y') if cadastro.data_cadastro else '',
            'hora_cadastro': cadastro.hora_cadastro.strftime('%H:%M:%S') if cadastro.hora_cadastro else '',
            'latitude': cadastro.latitude,
            'longitude': cadastro.longitude,
            'cidade': obter_cidade(cadastro),
            'status_sincronizacao': cadastro.status_sincronizacao,
            'dados_extras': json.dumps(cadastro.dados_extras or {}, ensure_ascii=False),
        })

    return linhas


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

        writer.writerow([
            'ID Ponto',
            'Nome Cadastrador',
            'Data Cadastro',
            'Hora Cadastro',
            'Latitude',
            'Longitude',
            'Cidade',
            'Status Sincronização',
            'Dados Extras',
        ])

        for linha in obter_linhas_exportacao(queryset):
            writer.writerow([
                linha['id_ponto'],
                linha['nome_cadastrador'],
                linha['data_cadastro'],
                linha['hora_cadastro'],
                linha['latitude'],
                linha['longitude'],
                linha['cidade'],
                linha['status_sincronizacao'],
                linha['dados_extras'],
            ])

        return response

    def exportar_excel(self, queryset):
        wb = Workbook()
        ws = wb.active
        ws.title = 'Cadastros'

        ws.append([
            'ID Ponto',
            'Nome Cadastrador',
            'Data Cadastro',
            'Hora Cadastro',
            'Latitude',
            'Longitude',
            'Cidade',
            'Status Sincronização',
            'Dados Extras',
        ])

        for linha in obter_linhas_exportacao(queryset):
            ws.append([
                linha['id_ponto'],
                linha['nome_cadastrador'],
                linha['data_cadastro'],
                linha['hora_cadastro'],
                linha['latitude'],
                linha['longitude'],
                linha['cidade'],
                linha['status_sincronizacao'],
                linha['dados_extras'],
            ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="cadastros_filtrados.xlsx"'
        wb.save(response)
        return response

    def exportar_kml(self, queryset):
        kml = simplekml.Kml()

        for cadastro in queryset:
            if cadastro.longitude is None or cadastro.latitude is None:
                continue

            cidade = obter_cidade(cadastro)
            descricao = (
                f"ID Ponto: {cadastro.id_ponto}\n"
                f"Cadastrador: {cadastro.nome_cadastrador}\n"
                f"Data: {cadastro.data_cadastro}\n"
                f"Hora: {cadastro.hora_cadastro}\n"
                f"Cidade: {cidade}\n"
                f"Status: {cadastro.status_sincronizacao}"
            )

            kml.newpoint(
                name=cadastro.id_ponto,
                coords=[(float(cadastro.longitude), float(cadastro.latitude))],
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