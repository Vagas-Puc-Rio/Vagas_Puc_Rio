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
    # Criamos as opções para o usuário escolher
    ESCOLHAS_TIPO = [
        ('aluno', 'Sou Aluno'),
        ('professor', 'Sou Professor')
    ]
    
    # Campo extra que só aparece no HTML, não vai pro banco direto
    tipo_conta = forms.ChoiceField(
        choices=ESCOLHAS_TIPO, 
        widget=forms.RadioSelect, # Cria aquelas "bolinhas" de marcar
        label="Você é:"
    )

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'senha']
        widgets = {
            'senha': forms.PasswordInput() # Esconde a senha com asteriscos
        }




