from django.db import models


class Cadastro(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("sincronizado", "Sincronizado"),
        ("erro", "Erro"),
    ]

    id_ponto = models.CharField(max_length=50, unique=True)
    nome_cadastrador = models.CharField(max_length=150)
    data_cadastro = models.DateField()
    hora_cadastro = models.TimeField()
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    dados_extras = models.JSONField(default=dict, blank=True)
    status_sincronizacao = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pendente"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cadastro"
        verbose_name_plural = "Cadastros"
        ordering = ["-criado_em"]

    def __str__(self):
        return self.id_ponto


class CampoFormulario(models.Model):
    TIPO_CHOICES = [
        ("texto", "Texto"),
        ("numero", "Número"),
        ("lista", "Lista Suspensa"),
        ("data", "Data"),
        ("hora", "Hora"),
        ("booleano", "Sim/Não"),
        ("textarea", "Texto Longo"),
    ]

    nome_interno = models.CharField(max_length=100, unique=True)
    rotulo = models.CharField(max_length=150)
    tipo_campo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    obrigatorio = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0)
    usa_lista_opcoes = models.BooleanField(default=False)
    placeholder = models.CharField(max_length=150, blank=True, default="")

    class Meta:
        verbose_name = "Campo do Formulário"
        verbose_name_plural = "Campos do Formulário"
        ordering = ["ordem", "id"]

    def __str__(self):
        return self.rotulo


class OpcaoCampo(models.Model):
    campo = models.ForeignKey(
        CampoFormulario,
        on_delete=models.CASCADE,
        related_name="opcoes"
    )
    valor = models.CharField(max_length=150)
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Opção do Campo"
        verbose_name_plural = "Opções do Campo"
        ordering = ["campo", "ordem", "id"]

    def __str__(self):
        return f"{self.campo.rotulo} - {self.valor}"


class FotoCadastro(models.Model):
    cadastro = models.ForeignKey(
        Cadastro,
        on_delete=models.CASCADE,
        related_name="fotos"
    )
    foto = models.ImageField(upload_to="fotos_cadastros/")
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foto do Cadastro"
        verbose_name_plural = "Fotos do Cadastro"
        ordering = ["id"]

    def __str__(self):
        return f"Foto - {self.cadastro.id_ponto}"