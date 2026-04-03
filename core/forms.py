from django import forms
from .models import Cadastro


class CadastroForm(forms.ModelForm):
    class Meta:
        model = Cadastro
        fields = [
            "id_ponto",
            "nome_cadastrador",
            "data_cadastro",
            "hora_cadastro",
            "latitude",
            "longitude",
            "status_sincronizacao",
        ]
        widgets = {
            "data_cadastro": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "hora_cadastro": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "id_ponto": forms.TextInput(attrs={"class": "form-control"}),
            "nome_cadastrador": forms.TextInput(attrs={"class": "form-control"}),
            "latitude": forms.NumberInput(attrs={"class": "form-control", "step": "0.0000001"}),
            "longitude": forms.NumberInput(attrs={"class": "form-control", "step": "0.0000001"}),
            "status_sincronizacao": forms.Select(attrs={"class": "form-control"}),
        }