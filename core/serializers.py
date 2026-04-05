from rest_framework import serializers
from .models import Cadastro, CampoFormulario, OpcaoCampo


class OpcaoCampoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcaoCampo
        fields = ['id', 'valor', 'ordem', 'ativo']


class CampoFormularioSerializer(serializers.ModelSerializer):
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


class CadastroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cadastro
        fields = [
            'id',
            'id_ponto',
            'nome_cadastrador',
            'usuario',
            'data_cadastro',
            'hora_cadastro',
            'latitude',
            'longitude',
            'status_sincronizacao',
            'dados_extras',
            'foto_1',
            'foto_2',
            'foto_3',
            'foto_4',
            'foto_5',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em']