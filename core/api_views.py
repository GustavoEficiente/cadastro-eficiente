from datetime import datetime
import uuid

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Cidade, CampoFormulario, Cadastro
from .api import CidadeSerializer, CampoSerializer, CadastroSerializer


def gerar_id_ponto():
    agora = datetime.now()
    sufixo = str(uuid.uuid4())[:4].upper()
    return f'CEF-{agora.strftime("%Y%m%d-%H%M%S")}-{sufixo}'


@api_view(['POST'])
def login_api(request):
    user = authenticate(
        username=request.data.get('username'),
        password=request.data.get('password')
    )

    if user:
        return Response({
            'status': 'ok',
            'user_id': user.id,
            'username': user.username
        })

    return Response({'status': 'erro'}, status=401)


@api_view(['GET'])
def cidades_api(request):
    cidades = Cidade.objects.all()
    return Response(CidadeSerializer(cidades, many=True).data)


@api_view(['GET'])
def campos_api(request):
    campos = CampoFormulario.objects.filter(ativo=True)
    return Response(CampoSerializer(campos, many=True).data)


@api_view(['GET'])
def cadastros_api(request):
    cadastros = Cadastro.objects.all().order_by('-criado_em')[:100]
    return Response(CadastroSerializer(cadastros, many=True).data)


@api_view(['POST'])
def cadastro_api(request):
    user_id = request.data.get('user_id')

    try:
        usuario = User.objects.get(id=user_id)
    except:
        return Response({'erro': 'Usuário inválido'}, status=400)

    payload = request.data.copy()

    agora = datetime.now()

    payload['id_ponto'] = gerar_id_ponto()
    payload['usuario'] = usuario.id
    payload['nome_cadastrador'] = usuario.username
    payload['data_cadastro'] = agora.date()
    payload['hora_cadastro'] = agora.strftime('%H:%M:%S')

    serializer = CadastroSerializer(data=payload)

    if serializer.is_valid():
        serializer.save()
        return Response({'status': 'ok'})

    return Response(serializer.errors, status=400)