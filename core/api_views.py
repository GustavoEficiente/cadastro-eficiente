from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import CampoFormulario, Cadastro, PerfilUsuario, FotoCadastro
from .api import CampoSerializer, CadastroSerializer


def gerar_id_ponto():
    agora = timezone.localtime()
    return f'CEF-{agora.strftime("%Y%m%d-%H%M%S-%f")[:21]}'


@api_view(['POST'])
@permission_classes([AllowAny])
def login_app(request):
    username = request.data.get('username')
    password = request.data.get('password')

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

    try:
        perfil = PerfilUsuario.objects.get(user=user)
    except PerfilUsuario.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Perfil do usuário não encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if perfil.tipo_usuario != 'cadastrador_app' and perfil.tipo_usuario != 'admin_site':
        return Response(
            {'success': False, 'message': 'Usuário sem acesso ao app.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if not perfil.ativo_no_app:
        return Response(
            {'success': False, 'message': 'Usuário sem acesso ao app.'},
            status=status.HTTP_403_FORBIDDEN
        )

    return Response(
        {
            'success': True,
            'username': user.username,
            'nome_exibicao': perfil.nome_exibicao,
            'user_id': user.id,
            'pode_cadastrar': perfil.pode_cadastrar,
            'pode_sincronizar': perfil.pode_sincronizar,
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
    cadastros = Cadastro.objects.all().order_by('-data_cadastro', '-hora_cadastro')
    serializer = CadastroSerializer(cadastros, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def criar_cadastro(request):
    dados = request.data.copy()

    username = dados.get('username')
    if not username:
        return Response(
            {'success': False, 'message': 'O campo username é obrigatório.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Usuário informado não existe.'},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        perfil = PerfilUsuario.objects.get(user=user)
    except PerfilUsuario.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Perfil do usuário não encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if not perfil.pode_cadastrar:
        return Response(
            {'success': False, 'message': 'Usuário sem permissão para cadastrar.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if not dados.get('id_ponto'):
        dados['id_ponto'] = gerar_id_ponto()

    dados['usuario'] = user.id
    dados['nome_cadastrador'] = perfil.nome_exibicao
    dados['sistema_coordenadas'] = 'sirgas2000'

    serializer = CadastroSerializer(data=dados)

    if serializer.is_valid():
        cadastro = serializer.save()

        for i in range(1, 6):
            arquivo = request.FILES.get(f'foto_{i}')
            if arquivo:
                FotoCadastro.objects.create(
                    cadastro=cadastro,
                    imagem=arquivo,
                    ordem=i
                )

        return Response(
            {
                'success': True,
                'message': 'Cadastro recebido com sucesso.',
                'id': cadastro.id,
                'id_ponto': cadastro.id_ponto,
                'usuario': user.username,
                'nome_cadastrador': perfil.nome_exibicao
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        {
            'success': False,
            'errors': serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )