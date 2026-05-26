from django import forms
from .models import Aluno, Professor, Instituicao, Usuario, Vaga



class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = '__all__' # Puxa todos os campos do Aluno

class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = '__all__' # Puxa todos os campos do Professor

class InstituicaoForm(forms.ModelForm):
    class Meta:
        model = Instituicao
        fields = '__all__'

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'
from django import forms
from .models import Usuario

class CadastroInicialForm(forms.ModelForm):

    ESCOLHAS_TIPO = [
        ('aluno', 'Sou Aluno'),
        ('professor', 'Sou Professor')
    ]

    tipo_conta = forms.ChoiceField(
        choices=ESCOLHAS_TIPO,
        widget=forms.RadioSelect,
        label="Você é:"
    )

    confirmar_senha = forms.CharField(
        widget=forms.PasswordInput(),
        label="Confirmar senha"
    )

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'senha', 'confirmar_senha']

        widgets = {
            'senha': forms.PasswordInput()
        }

    def clean(self):
        cleaned_data = super().clean()

        senha = cleaned_data.get("senha")
        confirmar = cleaned_data.get("confirmar_senha")

        if senha != confirmar:
            raise forms.ValidationError("As senhas não coincidem.")

        return cleaned_data



