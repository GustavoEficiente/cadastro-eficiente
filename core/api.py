from rest_framework import serializers
from .models import Cadastro, CampoFormulario, OpcaoCampo, FotoCadastro


class OpcaoCampoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcaoCampo
        fields = ['id', 'valor', 'ordem', 'ativo']


class CampoSerializer(serializers.ModelSerializer):
    opcoes = OpcaoCampoSerializer(many=True, read_only=True)

    class Meta:
        model = CampoFormulario
        fields = [
            'id',
            'nome_interno',
            'rotulo',
            'tipo_campo',
            'obrigatorio',
            'ativo',
            'ordem',
            'usa_lista_opcoes',
            'opcoes',
        ]


class FotoCadastroSerializer(serializers.ModelSerializer):
    class Meta:
        model = FotoCadastro
        fields = ['id', 'imagem', 'ordem', 'criado_em']


class CadastroSerializer(serializers.ModelSerializer):
    cidade_nome = serializers.CharField(source='cidade.nome', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    fotos = FotoCadastroSerializer(many=True, read_only=True)

    class Meta:
        model = Cadastro
        fields = [
            'id',
            'id_ponto',
            'cidade',
            'cidade_nome',
            'usuario',
            'usuario_username',
            'nome_cadastrador',
            'data_cadastro',
            'hora_cadastro',
            'latitude',
            'longitude',
            'tipo_coordenada',
            'sistema_coordenadas',
            'status_sincronizacao',
            'dados_extras',
            'fotos',
            'criado_em',
            'atualizado_em',
        ]