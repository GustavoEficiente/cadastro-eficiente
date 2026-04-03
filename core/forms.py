from django import forms
from .models import Cadastro


class CadastroForm(forms.ModelForm):
    foto_1 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": "image/*",
            "capture": "environment",
        })
    )
    foto_2 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": "image/*",
            "capture": "environment",
        })
    )
    foto_3 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": "image/*",
            "capture": "environment",
        })
    )
    foto_4 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": "image/*",
            "capture": "environment",
        })
    )
    foto_5 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": "image/*",
            "capture": "environment",
        })
    )

    class Meta:
        model = Cadastro
        fields = [
            "nome_cadastrador",
            "data_cadastro",
            "hora_cadastro",
            "latitude",
            "longitude",
            "status_sincronizacao",
        ]
        widgets = {
            "nome_cadastrador": forms.TextInput(attrs={"class": "form-control"}),
            "data_cadastro": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "hora_cadastro": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "latitude": forms.NumberInput(attrs={"class": "form-control", "step": "0.0000001"}),
            "longitude": forms.NumberInput(attrs={"class": "form-control", "step": "0.0000001"}),
            "status_sincronizacao": forms.Select(attrs={"class": "form-control"}),
        }