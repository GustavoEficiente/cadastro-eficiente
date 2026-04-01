from django.db import models
from django.contrib.auth.models import User


class Cidade(models.Model):
    nome = models.CharField(max_length=150)
    uf = models.CharField(max_length=2)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome}/{self.uf}'


class Cadastro(models.Model):
    TIPOS_COORDENADA = [
        ('decimal', 'Decimal'),
        ('gms', 'GMS'),
        ('utm', 'UTM'),
    ]

    id_ponto = models.CharField(max_length=50, unique=True)

    cidade = models.ForeignKey(
        Cidade,
        on_delete=models.PROTECT,
        related_name='cadastros',
        null=True,
        blank=True
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='cadastros',
        null=True,
        blank=True
    )

    nome_cadastrador = models.CharField(max_length=150, blank=True, default='')
    data_cadastro = models.DateField()
    hora_cadastro = models.TimeField()

    tipo_coordenada = models.CharField(
        max_length=20,
        choices=TIPOS_COORDENADA,
        default='decimal'
    )

    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    coordenada_texto = models.CharField(max_length=255, blank=True, default='')
    status_sincronizacao = models.CharField(max_length=30, default='pendente')
    dados_extras = models.JSONField(default=dict, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cadastro'
        verbose_name_plural = 'Cadastros'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.id_ponto} - {self.cidade}'


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
        verbose_name = 'Campo formulário'
        verbose_name_plural = 'Campos formulário'
        ordering = ['ordem', 'rotulo']

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
        verbose_name = 'Opção campo'
        verbose_name_plural = 'Opções campo'
        ordering = ['campo', 'ordem', 'valor']

    def __str__(self):
        return f'{self.campo.rotulo} - {self.valor}'