from django import forms
from .models import Aluno, Professor, Instituicao, Usuario, Vaga



class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = '__all__' # Puxa todos os campos do Aluno
        
class AlunoPerfilForm(forms.ModelForm):
    # Campos que não estão direto no model Aluno, mas precisamos (como Nome)
    nome_completo = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'placeholder': 'Ex: João da Silva', 'class': 'form-input'}))
    telefone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': '(21) 99999-0000', 'class': 'form-input'}))
    
    # Campo extra para o sobre
    sobre_voce = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Conte um pouco sobre seus objetivos e habilidades', 'class': 'form-input', 'rows': 4}), required=False)

    class Meta:
        model = Aluno
        fields = [
            'cpf', 'matricula', 'curso', 'periodo', 'tipo_interesse', 
            'linguagens', 'areas_atuacao'
        ]
        widgets = {
            'cpf': forms.TextInput(attrs={'placeholder': '000.000.000-00', 'class': 'form-input'}),
            'matricula': forms.TextInput(attrs={'placeholder': 'Ex: 2210123', 'class': 'form-input'}),
            'curso': forms.Select(attrs={'class': 'form-input'}),
            'periodo': forms.Select(attrs={'class': 'form-input'}), # Se periodo for integer no model, remova esse widget
            'tipo_interesse': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-horizontal'}),
            'linguagens': forms.CheckboxSelectMultiple(attrs={'class': 'tag-checkboxes'}),
            'areas_atuacao': forms.CheckboxSelectMultiple(attrs={'class': 'tag-checkboxes'}),
        }
        
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



