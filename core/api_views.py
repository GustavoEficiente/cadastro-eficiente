import json

from django.contrib.auth import authenticate

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Cadastro
from .serializers import CadastroSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login_app(request):
    username = request.data.get('username') or request.data.get('usuario')
    password = request.data.get('password') or request.data.get('senha')

    if not username or not password:
        return Response(
            {'success': False, 'message': 'Usuário e senha são obrigatórios.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if not user:
        return Response(
            {'success': False, 'message': 'Usuário ou senha inválidos.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    return Response(
        {
            'success': True,
            'ok': True,
            'username': user.username,
            'nome_exibicao': user.username,
            'usuario': user.username,
            'nome': user.username,
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_cadastros(request):
    cadastros = Cadastro.objects.all().order_by('-data_cadastro', '-hora_cadastro', '-id')
    serializer = CadastroSerializer(cadastros, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_campos(request):
    # O app abaixo usa form estático; esse endpoint continua existindo para não quebrar nada.
    return Response([])


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def criar_cadastro(request):
    data = request.data.copy()

    dados_extras = data.get('dados_extras')
    if isinstance(dados_extras, str):
        try:
            data['dados_extras'] = json.loads(dados_extras)
        except Exception:
            data['dados_extras'] = {}

    serializer = CadastroSerializer(data=data)

    if serializer.is_valid():
        cadastro = serializer.save(
            status_sincronizacao=request.data.get('status_sincronizacao', 'Sincronizado')
        )

        foto_file = request.FILES.get('foto')
        if foto_file:
            cadastro.foto.save(foto_file.name, foto_file, save=True)

        return Response(
            {
                'success': True,
                'ok': True,
                'message': 'Cadastro recebido com sucesso.',
                'id': cadastro.id,
                'id_ponto': cadastro.id_ponto,
                'tem_foto': bool(cadastro.foto),
                'foto_url': cadastro.foto.url if cadastro.foto else None,
                'request_files': list(request.FILES.keys()),
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        {
            'success': False,
            'ok': False,
            'errors': serializer.errors,
            'recebeu_arquivo_foto': 'foto' in request.FILES,
            'request_files': list(request.FILES.keys()),
        },
        status=status.HTTP_400_BAD_REQUEST
    )