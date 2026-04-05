from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import CampoFormulario, Cadastro
from .api import CampoSerializer, CadastroSerializer

# 🔥 IMPORTS PARA FOTO
import base64
from django.core.files.base import ContentFile


# =========================
# LOGIN (COMPATÍVEL COM APK)
# =========================
@api_view(['POST'])
@permission_classes([AllowAny])
def login_app(request):
    usuario = request.data.get('usuario')
    senha = request.data.get('senha')

    return Response({
        'ok': True,
        'usuario': usuario,
        'nome': usuario
    })


# =========================
# LISTAR CAMPOS
# =========================
@api_view(['GET'])
@permission_classes([AllowAny])
def listar_campos(request):
    campos = CampoFormulario.objects.filter(ativo=True).order_by('ordem')
    serializer = CampoSerializer(campos, many=True)
    return Response(serializer.data)


# =========================
# LISTAR CADASTROS
# =========================
@api_view(['GET'])
@permission_classes([AllowAny])
def listar_cadastros(request):
    cadastros = Cadastro.objects.all().order_by('-id')
    serializer = CadastroSerializer(cadastros, many=True)
    return Response(serializer.data)


# =========================
# CRIAR CADASTRO (COM FOTO - FINAL)
# =========================
@api_view(['POST'])
@permission_classes([AllowAny])
def criar_cadastro(request):

    data = request.data.copy()

    # 🔥 TENTA PEGAR FOTO COMO ARQUIVO
    foto = request.FILES.get('foto')

    # 🔥 SE NÃO VEIO ARQUIVO, TENTA BASE64
    foto_base64 = data.get('foto')

    if not foto and foto_base64:
        try:
            format, imgstr = foto_base64.split(';base64,')
            ext = format.split('/')[-1]

            foto = ContentFile(base64.b64decode(imgstr), name=f'foto.{ext}')
        except Exception:
            foto = None

    # 🔥 REMOVE FOTO DO DATA PARA NÃO QUEBRAR O SERIALIZER
    if 'foto' in data:
        data.pop('foto')

    serializer = CadastroSerializer(data=data)

    if serializer.is_valid():
        cadastro = serializer.save(
            status_sincronizacao=data.get('status_sincronizacao', 'Sincronizado')
        )

        # 🔥 SALVA FOTO SE EXISTIR
        if foto:
            cadastro.foto = foto
            cadastro.save()

        return Response({
            'ok': True,
            'mensagem': 'Cadastro salvo com sucesso',
            'id': cadastro.id,
            'id_ponto': cadastro.id_ponto
        }, status=status.HTTP_201_CREATED)

    return Response({
        'ok': False,
        'mensagem': 'Erro ao salvar cadastro',
        'erros': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)