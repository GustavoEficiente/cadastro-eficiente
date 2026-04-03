from rest_framework import serializers
from .models import Cadastro, CampoFormulario, OpcaoCampo, FotoCadastro


class OpcaoCampoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcaoCampo
        fields = ["id", "valor", "ordem", "ativo"]


class CampoSerializer(serializers.ModelSerializer):
    opcoes = OpcaoCampoSerializer(many=True, read_only=True)

    class Meta:
        model = CampoFormulario
        fields = [
            "id",
            "nome_interno",
            "rotulo",
            "tipo_campo",
            "obrigatorio",
            "ativo",
            "ordem",
            "usa_lista_opcoes",
            "placeholder",
            "opcoes",
        ]


class FotoCadastroSerializer(serializers.ModelSerializer):
    class Meta:
        model = FotoCadastro
        fields = ["id", "foto", "criada_em"]


class CadastroSerializer(serializers.ModelSerializer):
    fotos = FotoCadastroSerializer(many=True, read_only=True)

    class Meta:
        model = Cadastro
        fields = [
            "id",
            "id_ponto",
            "nome_cadastrador",
            "data_cadastro",
            "hora_cadastro",
            "latitude",
            "longitude",
            "dados_extras",
            "status_sincronizacao",
            "criado_em",
            "atualizado_em",
            "fotos",
        ]