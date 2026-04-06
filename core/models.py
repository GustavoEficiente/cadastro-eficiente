from django.db import models


class Cadastro(models.Model):
    id_ponto = models.CharField(max_length=50, unique=True)
    nome_cadastrador = models.CharField(max_length=150)
    data_cadastro = models.DateField()
    hora_cadastro = models.TimeField()
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    foto = models.ImageField(upload_to='fotos/', null=True, blank=True)
    status_sincronizacao = models.CharField(max_length=30, default='pendente')
    dados_extras = models.JSONField(default=dict, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id_ponto