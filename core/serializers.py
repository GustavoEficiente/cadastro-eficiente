from rest_framework import serializers
from .models import Cadastro


class CadastroSerializer(serializers.ModelSerializer):
    # Campo que pode vir do app
    usuario = serializers.CharField(write_only=True, required=False)

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

        # Se o app mandar "usuario" e não mandar "nome_cadastrador",
        # salva o valor de usuario em nome_cadastrador
        if usuario and not attrs.get('nome_cadastrador'):
            attrs['nome_cadastrador'] = usuario

        return attrs