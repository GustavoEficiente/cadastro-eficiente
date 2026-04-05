import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Cadastro, CampoFormulario, OpcaoCampo
from .serializers import CadastroSerializer


@api_view(['GET'])
def listar_campos(request):
    campos = CampoFormulario.objects.filter(ativo=True).order_by('ordem')

    resultado = []
    for campo in campos:
        opcoes = []
        if campo.usa_lista_opcoes:
            opcoes = list(
                campo.opcoes.filter(ativo=True).order_by('ordem').values_list('valor', flat=True)
            )

        resultado.append({
            'id': campo.id,
            'nome_interno': campo.nome_interno,
            'rotulo': campo.rotulo,
            'tipo_campo': campo.tipo_campo,
            'obrigatorio': campo.obrigatorio,
            'ativo': campo.ativo,
            'ordem': campo.ordem,
            'usa_lista_opcoes': campo.usa_lista_opcoes,
            'opcoes': opcoes,
        })

    return Response(resultado)


@api_view(['GET'])
def listar_cadastros(request):
    cadastros = Cadastro.objects.all().order_by('-criado_em')
    serializer = CadastroSerializer(cadastros, many=True)
    return Response(serializer.data)


@csrf_exempt
@require_http_methods(["POST"])
def sincronizar_cadastro(request):
    try:
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST.dict()

        serializer = CadastroSerializer(data=data)

        if serializer.is_valid():
            cadastro = serializer.save()
            return JsonResponse({
                'ok': True,
                'mensagem': 'Cadastro sincronizado com sucesso.',
                'id': cadastro.id,
                'id_ponto': cadastro.id_ponto,
            }, status=201)

        return JsonResponse({
            'ok': False,
            'mensagem': 'Erro de validação.',
            'erros': serializer.errors,
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'ok': False,
            'mensagem': 'Erro interno ao processar cadastro.',
            'erro': str(e),
        }, status=500)