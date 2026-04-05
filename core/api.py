from rest_framework import serializers
from .models import Cadastro, CampoFormulario, OpcaoCampo


class OpcaoCampoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcaoCampo
        fields = ['id', 'valor', 'ordem', 'ativo']


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
        if not obj.usa_lista_opcoes:
            return []
        opcoes = obj.opcoes.filter(ativo=True).order_by('ordem', 'valor')
        return OpcaoCampoSerializer(opcoes, many=True).data


class CadastroSerializer(serializers.ModelSerializer):
    usuario = serializers.CharField(write_only=True, required=False, allow_blank=True)

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
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em']

    def validate(self, attrs):
        usuario = attrs.pop('usuario', None)
        if usuario and not attrs.get('nome_cadastrador'):
            attrs['nome_cadastrador'] = usuario
        return attrs