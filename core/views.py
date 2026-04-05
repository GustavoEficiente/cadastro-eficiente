import csv
import json
from io import BytesIO

import pandas as pd
from django.http import HttpResponse
from django.contrib.auth import authenticate

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status

from .models import Cadastro, CampoFormulario
from .serializers import CadastroSerializer, CampoFormularioSerializer


@api_view(['POST'])
def api_login(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '').strip()

    user = authenticate(username=username, password=password)

    if user is not None:
        return Response({
            'ok': True,
            'mensagem': 'Login realizado com sucesso.',
            'usuario_id': user.id,
            'username': user.username,
        })

    return Response({
        'ok': False,
        'mensagem': 'Usuário ou senha inválidos.',
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def api_campos(request):
    campos = CampoFormulario.objects.filter(ativo=True).order_by('ordem', 'rotulo')
    serializer = CampoFormularioSerializer(campos, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def api_cadastro(request):
    try:
        # Converte request.data para dict normal
        dados = {}

        for chave in request.data.keys():
            dados[chave] = request.data.get(chave)

        # Trata dados_extras corretamente
        dados_extras = dados.get('dados_extras', '{}')
        if isinstance(dados_extras, str):
            try:
                dados['dados_extras'] = json.loads(dados_extras)
            except Exception:
                dados['dados_extras'] = {}
        elif isinstance(dados_extras, dict):
            dados['dados_extras'] = dados_extras
        else:
            dados['dados_extras'] = {}

        # Trata latitude/longitude vazias
        if dados.get('latitude') in ['', 'null', 'None', None]:
            dados['latitude'] = None

        if dados.get('longitude') in ['', 'null', 'None', None]:
            dados['longitude'] = None

        # Trata hora sem segundos
        hora = dados.get('hora_cadastro')
        if isinstance(hora, str) and hora:
            if len(hora) == 5:  # HH:MM
                dados['hora_cadastro'] = f'{hora}:00'

        # Inclui arquivos, se vierem
        for campo_foto in ['foto_1', 'foto_2', 'foto_3', 'foto_4', 'foto_5']:
            if campo_foto in request.FILES:
                dados[campo_foto] = request.FILES[campo_foto]

        serializer = CadastroSerializer(data=dados)

        if serializer.is_valid():
            cadastro = serializer.save(status_sincronizacao='sincronizado')
            return Response({
                'ok': True,
                'mensagem': 'Cadastro sincronizado com sucesso.',
                'id': cadastro.id,
                'id_ponto': cadastro.id_ponto,
            }, status=status.HTTP_201_CREATED)

        print('ERROS DO CADASTRO:', serializer.errors)

        return Response({
            'ok': False,
            'mensagem': 'Erro ao salvar cadastro.',
            'erros': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print('ERRO GERAL API CADASTRO:', str(e))
        return Response({
            'ok': False,
            'mensagem': 'Erro interno ao processar cadastro.',
            'erro': str(e),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def api_cadastros(request):
    cadastros = Cadastro.objects.all().order_by('-criado_em')
    serializer = CadastroSerializer(cadastros, many=True, context={'request': request})
    return Response(serializer.data)


def _url_absoluta(request, arquivo):
    if arquivo:
        return request.build_absolute_uri(arquivo.url)
    return ''


@api_view(['GET'])
def exportar_excel(request):
    cadastros = Cadastro.objects.all().order_by('-criado_em')

    dados = []
    for c in cadastros:
        dados.append({
            'id_ponto': c.id_ponto,
            'nome_cadastrador': c.nome_cadastrador,
            'data_cadastro': c.data_cadastro.strftime('%Y-%m-%d') if c.data_cadastro else '',
            'hora_cadastro': c.hora_cadastro.strftime('%H:%M:%S') if c.hora_cadastro else '',
            'latitude': c.latitude,
            'longitude': c.longitude,
            'status_sincronizacao': c.status_sincronizacao,
            'foto_1': _url_absoluta(request, c.foto_1),
            'foto_2': _url_absoluta(request, c.foto_2),
            'foto_3': _url_absoluta(request, c.foto_3),
            'foto_4': _url_absoluta(request, c.foto_4),
            'foto_5': _url_absoluta(request, c.foto_5),
            'dados_extras': str(c.dados_extras),
        })

    df = pd.DataFrame(dados)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Cadastros')
        ws = writer.sheets['Cadastros']

        colunas_fotos = ['H', 'I', 'J', 'K', 'L']
        for col in colunas_fotos:
            for cell in ws[col][1:]:
                if cell.value:
                    cell.hyperlink = cell.value
                    cell.style = 'Hyperlink'

    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="relatorio_cadastros.xlsx"'
    return response


@api_view(['GET'])
def exportar_csv(request):
    cadastros = Cadastro.objects.all().order_by('-criado_em')

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="relatorio_cadastros.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'id_ponto',
        'nome_cadastrador',
        'data_cadastro',
        'hora_cadastro',
        'latitude',
        'longitude',
        'status_sincronizacao',
        'foto_1',
        'foto_2',
        'foto_3',
        'foto_4',
        'foto_5',
        'dados_extras',
    ])

    for c in cadastros:
        writer.writerow([
            c.id_ponto,
            c.nome_cadastrador,
            c.data_cadastro.strftime('%Y-%m-%d') if c.data_cadastro else '',
            c.hora_cadastro.strftime('%H:%M:%S') if c.hora_cadastro else '',
            c.latitude,
            c.longitude,
            c.status_sincronizacao,
            _url_absoluta(request, c.foto_1),
            _url_absoluta(request, c.foto_2),
            _url_absoluta(request, c.foto_3),
            _url_absoluta(request, c.foto_4),
            _url_absoluta(request, c.foto_5),
            str(c.dados_extras),
        ])

    return response