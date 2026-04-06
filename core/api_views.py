from django.contrib.auth import authenticate

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import CampoFormulario, Cadastro
from .api import CampoSerializer, CadastroSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login_app(request):
    username = request.data.get('username') or request.data.get('usuario')
    password = request.data.get('password') or request.data.get('senha')

    if not username or not password:
        return Response(
            {
                'success': False,
                'message': 'Usuário e senha são obrigatórios.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if not user:
        return Response(
            {
                'success': False,
                'message': 'Usuário ou senha inválidos.'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    return Response(
        {
            'success': True,
            'ok': True,
            'username': user.username,
            'nome_exibicao': user.username,
            'usuario': user.username,
            'nome': user.username
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_campos(request):
    campos = CampoFormulario.objects.filter(ativo=True).order_by('ordem', 'rotulo')
    serializer = CampoSerializer(campos, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_cadastros(request):
    cadastros = Cadastro.objects.all().order_by('-data_cadastro', '-hora_cadastro', '-id')
    serializer = CadastroSerializer(cadastros, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def criar_cadastro(request):
    serializer = CadastroSerializer(data=request.data)

    if serializer.is_valid():
        cadastro = serializer.save(
            status_sincronizacao=request.data.get('status_sincronizacao', 'Sincronizado')
        )
        return Response(
            {
                'success': True,
                'ok': True,
                'message': 'Cadastro recebido com sucesso.',
                'mensagem': 'Cadastro recebido com sucesso.',
                'id': cadastro.id,
                'id_ponto': cadastro.id_ponto,
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        {
            'success': False,
            'ok': False,
            'errors': serializer.errors,
            'erros': serializer.errors,
        },
        status=status.HTTP_400_BAD_REQUEST
    )