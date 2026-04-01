from datetime import datetime
import uuid
import csv
import ast

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
import simplekml

from .forms import CadastroForm
from .models import Cadastro, CampoFormulario


def gerar_id_ponto():
    agora = datetime.now()
    sufixo = str(uuid.uuid4())[:4].upper()
    return f'CEF-{agora.strftime("%Y%m%d-%H%M%S")}-{sufixo}'


def aplicar_filtros(request, queryset):
    cidade = request.GET.get('cidade')
    cadastrador = request.GET.get('cadastrador')
    data_inicial = request.GET.get('data_inicial')
    data_final = request.GET.get('data_final')

    if cidade:
        queryset = queryset.filter(cidade__nome__icontains=cidade)

    if cadastrador:
        queryset = queryset.filter(
            Q(nome_cadastrador__icontains=cadastrador) |
            Q(usuario__username__icontains=cadastrador)
        )

    if data_inicial:
        queryset = queryset.filter(data_cadastro__gte=data_inicial)

    if data_final:
        queryset = queryset.filter(data_cadastro__lte=data_final)

    filtros = {
        'cidade': cidade or '',
        'cadastrador': cadastrador or '',
        'data_inicial': data_inicial or '',
        'data_final': data_final or '',
    }

    return queryset, filtros


@login_required
def dashboard(request):
    total_cadastros = Cadastro.objects.count()
    total_pendentes = Cadastro.objects.filter(status_sincronizacao='pendente').count()
    total_usuario = Cadastro.objects.filter(usuario=request.user).count()

    context = {
        'total_cadastros': total_cadastros,
        'total_pendentes': total_pendentes,
        'total_usuario': total_usuario,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def novo_cadastro(request):
    campos = CampoFormulario.objects.filter(ativo=True).order_by('ordem')

    if request.method == 'POST':
        form = CadastroForm(request.POST)

        if form.is_valid():
            cadastro = form.save(commit=False)
            agora = datetime.now()

            cadastro.id_ponto = gerar_id_ponto()
            cadastro.usuario = request.user
            cadastro.nome_cadastrador = request.user.get_full_name() or request.user.username
            cadastro.data_cadastro = agora.date()
            cadastro.hora_cadastro = agora.time()
            cadastro.status_sincronizacao = 'pendente'

            dados_extras = {}

            for campo in campos:
                valor = request.POST.get(campo.nome_interno)

                if campo.tipo_campo == 'booleano':
                    if valor == 'sim':
                        valor = 'Sim'
                    elif valor == 'nao':
                        valor = 'Não'

                dados_extras[campo.nome_interno] = valor

            cadastro.dados_extras = dados_extras
            cadastro.save()

            messages.success(request, 'Cadastro realizado com sucesso.')
            return redirect('core:lista_cadastros')
    else:
        form = CadastroForm()

    context = {
        'form': form,
        'campos_dinamicos': campos,
        'modo_edicao': False,
        'dados_extras_existentes': {},
    }
    return render(request, 'core/novo_cadastro.html', context)


@login_required
def editar_cadastro(request, pk):
    cadastro = get_object_or_404(Cadastro, pk=pk)
    campos = CampoFormulario.objects.filter(ativo=True).order_by('ordem')

    if request.method == 'POST':
        form = CadastroForm(request.POST, instance=cadastro)

        if form.is_valid():
            cadastro = form.save(commit=False)

            dados_extras = {}

            for campo in campos:
                valor = request.POST.get(campo.nome_interno)

                if campo.tipo_campo == 'booleano':
                    if valor == 'sim':
                        valor = 'Sim'
                    elif valor == 'nao':
                        valor = 'Não'

                dados_extras[campo.nome_interno] = valor

            cadastro.dados_extras = dados_extras
            cadastro.save()

            messages.success(request, 'Cadastro atualizado com sucesso.')
            return redirect('core:lista_cadastros')
    else:
        form = CadastroForm(instance=cadastro)

    context = {
        'form': form,
        'campos_dinamicos': campos,
        'modo_edicao': True,
        'cadastro': cadastro,
        'dados_extras_existentes': cadastro.dados_extras or {},
    }
    return render(request, 'core/novo_cadastro.html', context)


@login_required
def lista_cadastros(request):
    cadastros = Cadastro.objects.select_related('cidade', 'usuario').all().order_by('-criado_em')
    cadastros, filtros = aplicar_filtros(request, cadastros)

    context = {
        'cadastros': cadastros,
        'filtros': filtros,
    }
    return render(request, 'core/lista_cadastros.html', context)


@login_required
def exportar_csv(request):
    cadastros = Cadastro.objects.select_related('cidade', 'usuario').all().order_by('-criado_em')
    cadastros, _ = aplicar_filtros(request, cadastros)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="cadastros.csv"'
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'ID Ponto',
        'Cidade',
        'Cadastrador',
        'Usuario',
        'Data',
        'Hora',
        'Tipo Coordenada',
        'Latitude',
        'Longitude',
        'Coordenada Texto',
        'Status',
        'Dados Extras',
    ])

    for cadastro in cadastros:
        writer.writerow([
            cadastro.id_ponto,
            str(cadastro.cidade) if cadastro.cidade else '',
            cadastro.nome_cadastrador,
            cadastro.usuario.username if cadastro.usuario else '',
            cadastro.data_cadastro,
            cadastro.hora_cadastro,
            cadastro.get_tipo_coordenada_display(),
            cadastro.latitude,
            cadastro.longitude,
            cadastro.coordenada_texto,
            cadastro.status_sincronizacao,
            str(cadastro.dados_extras),
        ])

    return response


@login_required
def exportar_excel(request):
    cadastros = Cadastro.objects.select_related('cidade', 'usuario').all().order_by('-criado_em')
    cadastros, _ = aplicar_filtros(request, cadastros)

    wb = Workbook()
    ws = wb.active
    ws.title = 'Cadastros'

    cabecalho = [
        'ID Ponto',
        'Cidade',
        'Cadastrador',
        'Usuario',
        'Data',
        'Hora',
        'Tipo Coordenada',
        'Latitude',
        'Longitude',
        'Coordenada Texto',
        'Status',
        'Dados Extras',
    ]
    ws.append(cabecalho)

    for cadastro in cadastros:
        ws.append([
            cadastro.id_ponto,
            str(cadastro.cidade) if cadastro.cidade else '',
            cadastro.nome_cadastrador,
            cadastro.usuario.username if cadastro.usuario else '',
            str(cadastro.data_cadastro),
            str(cadastro.hora_cadastro),
            cadastro.get_tipo_coordenada_display(),
            float(cadastro.latitude) if cadastro.latitude is not None else None,
            float(cadastro.longitude) if cadastro.longitude is not None else None,
            cadastro.coordenada_texto,
            cadastro.status_sincronizacao,
            str(cadastro.dados_extras),
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="cadastros.xlsx"'
    wb.save(response)
    return response


@login_required
def exportar_pdf(request):
    cadastros = Cadastro.objects.select_related('cidade', 'usuario').all().order_by('-criado_em')
    cadastros, filtros = aplicar_filtros(request, cadastros)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="cadastros.pdf"'

    pdf = canvas.Canvas(response, pagesize=landscape(A4))
    largura, altura = landscape(A4)

    pdf.setTitle('Relatório de Cadastros')

    y = altura - 40
    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(30, y, 'Cadastro Eficiente - Relatório de Cadastros')

    y -= 25
    pdf.setFont('Helvetica', 10)
    pdf.drawString(30, y, f"Cidade: {filtros['cidade'] or 'Todas'}")
    pdf.drawString(220, y, f"Cadastrador: {filtros['cadastrador'] or 'Todos'}")
    pdf.drawString(470, y, f"Período: {filtros['data_inicial'] or '---'} até {filtros['data_final'] or '---'}")

    y -= 30
    pdf.setFont('Helvetica-Bold', 9)
    pdf.drawString(30, y, 'ID')
    pdf.drawString(140, y, 'Cidade')
    pdf.drawString(240, y, 'Cadastrador')
    pdf.drawString(360, y, 'Data')
    pdf.drawString(430, y, 'Tipo Coord.')
    pdf.drawString(520, y, 'Latitude')
    pdf.drawString(640, y, 'Longitude')

    y -= 15
    pdf.line(30, y, largura - 30, y)

    for cadastro in cadastros:
        y -= 18
        if y < 40:
            pdf.showPage()
            y = altura - 40

        pdf.setFont('Helvetica', 8)
        pdf.drawString(30, y, str(cadastro.id_ponto)[:18])
        pdf.drawString(140, y, str(cadastro.cidade)[:18] if cadastro.cidade else '')
        pdf.drawString(240, y, str(cadastro.nome_cadastrador)[:20])
        pdf.drawString(360, y, str(cadastro.data_cadastro))
        pdf.drawString(430, y, str(cadastro.get_tipo_coordenada_display())[:12])
        pdf.drawString(520, y, str(cadastro.latitude)[:14] if cadastro.latitude is not None else '')
        pdf.drawString(640, y, str(cadastro.longitude)[:14] if cadastro.longitude is not None else '')

    pdf.save()
    return response


@login_required
def exportar_kml(request):
    cadastros = Cadastro.objects.select_related('cidade', 'usuario').all().order_by('-criado_em')
    cadastros, _ = aplicar_filtros(request, cadastros)

    kml = simplekml.Kml()

    for cadastro in cadastros:
        if cadastro.latitude is not None and cadastro.longitude is not None:
            pnt = kml.newpoint(
                name=str(cadastro.id_ponto),
                coords=[(float(cadastro.longitude), float(cadastro.latitude))]
            )

            descricao = (
                f"Cidade: {cadastro.cidade}\n"
                f"Cadastrador: {cadastro.nome_cadastrador}\n"
                f"Data: {cadastro.data_cadastro}\n"
                f"Hora: {cadastro.hora_cadastro}\n"
                f"Tipo Coordenada: {cadastro.get_tipo_coordenada_display()}\n"
                f"Status: {cadastro.status_sincronizacao}\n"
                f"Dados Extras: {cadastro.dados_extras}"
            )
            pnt.description = descricao

    response = HttpResponse(content_type='application/vnd.google-earth.kml+xml')
    response['Content-Disposition'] = 'attachment; filename="cadastros.kml"'
    response.write(kml.kml())
    return response