from django.db import models
from django.contrib.auth.models import User


class CampoFormulario(models.Model):
    TIPOS = [
        ('texto', 'Texto'),
        ('numero', 'Número'),
        ('lista', 'Lista Suspensa'),
        ('data', 'Data'),
        ('hora', 'Hora'),
        ('booleano', 'Sim/Não'),
        ('textarea', 'Texto Longo'),
    ]

    nome_interno = models.CharField(max_length=100, unique=True)
    rotulo = models.CharField(max_length=150)
    tipo_campo = models.CharField(max_length=20, choices=TIPOS)
    obrigatorio = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0)
    usa_lista_opcoes = models.BooleanField(default=False)

    class Meta:
        ordering = ['ordem', 'rotulo']
        verbose_name = 'Campo do formulário'
        verbose_name_plural = 'Campos do formulário'

    def __str__(self):
        return self.rotulo


class OpcaoCampo(models.Model):
    campo = models.ForeignKey(
        CampoFormulario,
        on_delete=models.CASCADE,
        related_name='opcoes'
    )
    valor = models.CharField(max_length=150)
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ['campo', 'ordem', 'valor']
        verbose_name = 'Opção do campo'
        verbose_name_plural = 'Opções do campo'

    def __str__(self):
        return f'{self.campo.rotulo} - {self.valor}'


class Cadastro(models.Model):
    STATUS_SYNC = [
        ('pendente', 'Pendente'),
        ('sincronizado', 'Sincronizado'),
        ('erro', 'Erro'),
    ]

    id_ponto = models.CharField(max_length=60, unique=True)
    nome_cadastrador = models.CharField(max_length=150)
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cadastros'
    )

    data_cadastro = models.DateField()
    hora_cadastro = models.TimeField()

    latitude = models.DecimalField(max_digits=11, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=7, null=True, blank=True)

    status_sincronizacao = models.CharField(
        max_length=30,
        choices=STATUS_SYNC,
        default='pendente'
    )

    dados_extras = models.JSONField(default=dict, blank=True)

    foto_1 = models.ImageField(upload_to='cadastros/fotos/', null=True, blank=True)
    foto_2 = models.ImageField(upload_to='cadastros/fotos/', null=True, blank=True)
    foto_3 = models.ImageField(upload_to='cadastros/fotos/', null=True, blank=True)
    foto_4 = models.ImageField(upload_to='cadastros/fotos/', null=True, blank=True)
    foto_5 = models.ImageField(upload_to='cadastros/fotos/', null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Cadastro'
        verbose_name_plural = 'Cadastros'

    def __str__(self):
        return self.id_ponto

    def get_fotos_urls(self, request=None):
        fotos = []
        for campo in ['foto_1', 'foto_2', 'foto_3', 'foto_4', 'foto_5']:
            arquivo = getattr(self, campo)
            if arquivo:
                if request:
                    fotos.append(request.build_absolute_uri(arquivo.url))
                else:
                    fotos.append(arquivo.url)
            else:
                fotos.append('')
        return fotos