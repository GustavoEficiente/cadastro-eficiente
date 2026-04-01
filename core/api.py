from rest_framework import serializers
from .models import Cadastro, Cidade, CampoFormulario, OpcaoCampo


class OpcaoCampoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcaoCampo
        fields = ['id', 'valor', 'ordem', 'ativo']


class CidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cidade
        fields = ['id', 'nome', 'uf', 'ativo']


class CampoSerializer(serializers.ModelSerializer):
    opcoes = serializers.SerializerMethodField()

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

    def get_opcoes(self, obj):
        opcoes = obj.opcoes.filter(ativo=True).order_by('ordem', 'valor')
        return OpcaoCampoSerializer(opcoes, many=True).data


class CadastroSerializer(serializers.ModelSerializer):
    cidade_nome = serializers.SerializerMethodField()
    usuario_nome = serializers.SerializerMethodField()

    class Meta:
        model = Cadastro
        fields = [
            'id',
            'id_ponto',
            'cidade',
            'cidade_nome',
            'usuario',
            'usuario_nome',
            'nome_cadastrador',
            'data_cadastro',
            'hora_cadastro',
            'tipo_coordenada',
            'latitude',
            'longitude',
            'coordenada_texto',
            'status_sincronizacao',
            'dados_extras',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = [
            'usuario',
            'nome_cadastrador',
            'data_cadastro',
            'hora_cadastro',
            'criado_em',
            'atualizado_em',
        ]

    def get_cidade_nome(self, obj):
        return str(obj.cidade) if obj.cidade else ''

    def get_usuario_nome(self, obj):
        return obj.usuario.username if obj.usuario else ''