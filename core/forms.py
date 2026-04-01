from django import forms
from .models import Cadastro, Cidade


class CadastroForm(forms.ModelForm):
    class Meta:
        model = Cadastro
        fields = ['cidade', 'tipo_coordenada', 'latitude', 'longitude', 'coordenada_texto']
        widgets = {
            'cidade': forms.Select(attrs={'class': 'form-control'}),
            'tipo_coordenada': forms.Select(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0000001',
                'placeholder': 'Latitude'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0000001',
                'placeholder': 'Longitude'
            }),
            'coordenada_texto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: 03°43\'54"S / 38°31\'36"W ou UTM'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cidade'].queryset = Cidade.objects.filter(ativo=True).order_by('nome')