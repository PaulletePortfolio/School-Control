from django import forms
from .models import Recado

class RecadoForm(forms.ModelForm):
    class Meta:
        model = Recado
        fields = ['conteudo'] 
        widgets = {
            'conteudo': forms.Textarea(attrs={'placeholder': 'Digite o recado aqui...'})
        }
        