import csv
import io
import json
import uuid
from datetime import datetime

import pandas as pd
import simplekml

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

from .forms import CadastroForm
from .models import Cadastro, CampoFormulario


def gerar_id_ponto():
    agora = datetime.now()
    sufixo = str(uuid.uuid4())[:4].upper()
    return f"CEF-{agora.strftime('%Y%m%d-%H%M%S')}-{sufixo}"


def obter_campos_dinamicos():
    return CampoFormulario.objects.filter(ativo=True).order_by("ordem", "id")


@login_required
def dashboard(request):
    total_cadastros = Cadastro.objects.count()
    pendentes = Cadastro.objects.filter(status_sincronizacao="pendente").count()
    sincronizados = Cadastro.objects.filter(status_sincronizacao="sincronizado").count()
    campos_ativos = CampoFormulario.objects.filter(ativo=True).count()

    contexto = {
        "total_cadastros": total_cadastros,
        "pendentes": pendentes,
        "sincronizados": sincronizados,
        "campos_ativos": campos_ativos,
    }
    return render(request, "core/dashboard.html", contexto)


@login_required
def lista_cadastros(request):
    cadastros = Cadastro.objects.all().order_by("-criado_em")
    return render(request, "core/lista_cadastros.html", {"cadastros": cadastros})


@login_required
def novo_cadastro(request):
    campos_dinamicos = obter_campos_dinamicos()

    if request.method == "POST":
        form = CadastroForm(request.POST)

        if form.is_valid():
            cadastro = form.save(commit=False)
            cadastro.id_ponto = gerar_id_ponto()

            if not cadastro.data_cadastro:
                cadastro.data_cadastro = timezone.localdate()

            if not cadastro.hora_cadastro:
                cadastro.hora_cadastro = timezone.localtime().time()

            dados_extras = {}

            for campo in campos_dinamicos:
                valor = request.POST.get(campo.nome_interno, "")

                if campo.tipo_campo == "booleano":
                    valor = request.POST.get(campo.nome_interno) == "on"

                dados_extras[campo.nome_interno] = valor

            cadastro.dados_extras = dados_extras
            cadastro.save()

            messages.success(request, "Cadastro criado com sucesso.")
            return redirect("core:lista_cadastros")
    else:
        form = CadastroForm(
            initial={
                "data_cadastro": timezone.localdate(),
                "hora_cadastro": timezone.localtime().strftime("%H:%M"),
                "status_sincronizacao": "pendente",
            }
        )

    return render(
        request,
        "core/form_cadastro.html",
        {
            "form": form,
            "titulo": "Novo Cadastro",
            "campos_dinamicos": campos_dinamicos,
            "modo_edicao": False,
        },
    )


@login_required
def editar_cadastro(request, pk):
    cadastro = get_object_or_404(Cadastro, pk=pk)
    campos_dinamicos = obter_campos_dinamicos()

    if request.method == "POST":
        form = CadastroForm(request.POST, instance=cadastro)

        if form.is_valid():
            cadastro = form.save(commit=False)

            dados_extras = cadastro.dados_extras or {}

            for campo in campos_dinamicos:
                valor = request.POST.get(campo.nome_interno, "")

                if campo.tipo_campo == "booleano":
                    valor = request.POST.get(campo.nome_interno) == "on"

                dados_extras[campo.nome_interno] = valor

            cadastro.dados_extras = dados_extras
            cadastro.save()

            messages.success(request, "Cadastro atualizado com sucesso.")
            return redirect("core:lista_cadastros")
    else:
        form = CadastroForm(instance=cadastro)

    return render(
        request,
        "core/form_cadastro.html",
        {
            "form": form,
            "titulo": "Editar Cadastro",
            "campos_dinamicos": campos_dinamicos,
            "cadastro": cadastro,
            "modo_edicao": True,
        },
    )


def montar_linhas_exportacao():
    campos_dinamicos = list(obter_campos_dinamicos())
    cadastros = Cadastro.objects.all().order_by("-criado_em")

    linhas = []

    for cadastro in cadastros:
        linha = {
            "id_ponto": cadastro.id_ponto,
            "nome_cadastrador": cadastro.nome_cadastrador,
            "data_cadastro": cadastro.data_cadastro,
            "hora_cadastro": cadastro.hora_cadastro,
            "latitude": cadastro.latitude,
            "longitude": cadastro.longitude,
            "status_sincronizacao": cadastro.status_sincronizacao,
        }

        dados_extras = cadastro.dados_extras or {}

        for campo in campos_dinamicos:
            linha[campo.rotulo] = dados_extras.get(campo.nome_interno, "")

        linhas.append(linha)

    return linhas


@login_required
def exportar_csv(request):
    linhas = montar_linhas_exportacao()

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="cadastros.csv"'

    if not linhas:
        response.write("Nenhum cadastro encontrado.")
        return response

    writer = csv.DictWriter(response, fieldnames=linhas[0].keys())
    writer.writeheader()
    writer.writerows(linhas)

    return response


@login_required
def exportar_excel(request):
    linhas = montar_linhas_exportacao()

    df = pd.DataFrame(linhas)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="cadastros.xlsx"'

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Cadastros")

    return response


@login_required
def exportar_pdf(request):
    linhas = montar_linhas_exportacao()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="cadastros.pdf"'

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=landscape(A4))
    largura, altura = landscape(A4)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(30, altura - 30, "Cadastro Eficiente - Relatório de Cadastros")

    y = altura - 60
    pdf.setFont("Helvetica", 8)

    if not linhas:
        pdf.drawString(30, y, "Nenhum cadastro encontrado.")
    else:
        colunas = list(linhas[0].keys())
        x_positions = [30 + i * 90 for i in range(min(len(colunas), 8))]

        for i, coluna in enumerate(colunas[:8]):
            pdf.drawString(x_positions[i], y, str(coluna)[:18])

        y -= 20

        for linha in linhas[:35]:
            for i, coluna in enumerate(colunas[:8]):
                pdf.drawString(x_positions[i], y, str(linha.get(coluna, ""))[:18])
            y -= 16

            if y < 40:
                pdf.showPage()
                y = altura - 40

    pdf.save()
    pdf_data = buffer.getvalue()
    buffer.close()
    response.write(pdf_data)

    return response


@login_required
def exportar_kml(request):
    cadastros = Cadastro.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)

    kml = simplekml.Kml()

    for cadastro in cadastros:
        descricao = [
            f"ID: {cadastro.id_ponto}",
            f"Cadastrador: {cadastro.nome_cadastrador}",
            f"Data: {cadastro.data_cadastro}",
            f"Hora: {cadastro.hora_cadastro}",
            f"Status: {cadastro.status_sincronizacao}",
        ]

        if cadastro.dados_extras:
            for chave, valor in cadastro.dados_extras.items():
                descricao.append(f"{chave}: {valor}")

        pnt = kml.newpoint(
            name=cadastro.id_ponto,
            coords=[(float(cadastro.longitude), float(cadastro.latitude))],
        )
        pnt.description = "\n".join(descricao)

    response = HttpResponse(content_type="application/vnd.google-earth.kml+xml")
    response["Content-Disposition"] = 'attachment; filename="cadastros.kml"'
    response.write(kml.kml())

    return response