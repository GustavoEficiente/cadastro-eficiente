from datetime import datetime
import json
import uuid

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from .api import CampoSerializer, CadastroSerializer
from .models import CampoFormulario, Cadastro, FotoCadastro


def gerar_id_ponto():
    agora = datetime.now()
    sufixo = str(uuid.uuid4())[:4].upper()
    return f"CEF-{agora.strftime('%Y%m%d-%H%M%S')}-{sufixo}"


@api_view(["POST"])
def login_api(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is not None:
        return Response(
            {
                "success": True,
                "message": "Login realizado com sucesso.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                },
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {
            "success": False,
            "message": "Usuário ou senha inválidos.",
        },
        status=status.HTTP_401_UNAUTHORIZED,
    )


@api_view(["GET"])
def campos_api(request):
    campos = CampoFormulario.objects.filter(ativo=True).order_by("ordem", "id")
    serializer = CampoSerializer(campos, many=True)
    return Response(
        {
            "success": True,
            "results": serializer.data,
        }
    )


@api_view(["GET"])
def cadastros_api(request):
    cadastros = Cadastro.objects.all().order_by("-criado_em")
    serializer = CadastroSerializer(cadastros, many=True)
    return Response(
        {
            "success": True,
            "results": serializer.data,
        }
    )


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def cadastro_completo_api(request):
    try:
        dados_extras = request.data.get("dados_extras", "{}")

        if isinstance(dados_extras, str):
            dados_extras = json.loads(dados_extras or "{}")

        id_ponto = request.data.get("id_ponto") or gerar_id_ponto()

        cadastro = Cadastro.objects.create(
            id_ponto=id_ponto,
            nome_cadastrador=request.data.get("nome_cadastrador", ""),
            data_cadastro=request.data.get("data_cadastro"),
            hora_cadastro=request.data.get("hora_cadastro"),
            latitude=request.data.get("latitude") or None,
            longitude=request.data.get("longitude") or None,
            dados_extras=dados_extras,
            status_sincronizacao=request.data.get("status_sincronizacao", "sincronizado"),
        )

        fotos = request.FILES.getlist("fotos")
        for foto in fotos[:5]:
            FotoCadastro.objects.create(cadastro=cadastro, foto=foto)

        serializer = CadastroSerializer(cadastro)

        return Response(
            {
                "success": True,
                "message": "Cadastro salvo com sucesso.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response(
            {
                "success": False,
                "message": f"Erro ao salvar cadastro: {str(e)}",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )