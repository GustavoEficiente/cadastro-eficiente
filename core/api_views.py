from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import CampoFormulario, Cadastro
from .api import CampoSerializer, CadastroSerializer


# =========================
# LOGIN (COMPATÍVEL COM APK)
# =========================
@api_view(['POST'])
@permission_classes([AllowAny])
def criar_cadastro(request):
    serializer = CadastroSerializer(data=request.data)

    if serializer.is_valid():
        cadastro = serializer.save(
            status_sincronizacao=request.data.get('status_sincronizacao', 'Sincronizado')
        )

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
# CRIAR CADASTRO (COM FOTO)
# =========================
@api_view(['POST'])
@permission_classes([AllowAny])
def criar_cadastro(request):
    data = request.data.copy()

    # 🔥 captura a foto enviada
    foto = request.FILES.get('foto')

    serializer = CadastroSerializer(data=data)

    if serializer.is_valid():
        cadastro = serializer.save(
            status_sincronizacao=data.get('status_sincronizacao', 'Sincronizado')
        )

        # 🔥 salva a foto se existir
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