from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password, make_password

from usuarios.models import Usuario # Ferramenta nativa para criptografar
from .forms import CadastroInicialForm


def pagina_inicial(request):
    return render(request, 'usuarios/home.html')

def cadastro_inicial(request, tipo):
    if request.method == 'POST':
        form = CadastroInicialForm(request.POST)

        if form.is_valid():
            # commit=False significa: "Cria o objeto, mas espera, não salva no banco ainda!"
            usuario = form.save(commit=False) 
            
            # 1. FAZENDO DO JEITO CERTO: Criptografando a senha
            senha_pura = form.cleaned_data['senha']
            usuario.senha = make_password(senha_pura) 
            
          
            usuario.save() 
            
            # Envio de e-mail omitido aqui para encurtar, mas você mantém o seu código de send_mail!
            
            # 2. SEPARANDO ALUNO DE PROFESSOR
            tipo = form.cleaned_data['tipo_conta'] # Lê a opção que ele marcou
            
            if tipo == 'aluno':
                # Manda para a URL de completar perfil do aluno, passando o ID do usuário criado
                return redirect('primeiros_passos')
            else:
                # Manda para a URL de completar perfil do professor
                return redirect('completar_perfil_professor', usuario_id=usuario.id)
    else:
        form = CadastroInicialForm()
        
    return render(request, 'usuarios/cadastro_inicial.html', {'form': form, 'tipo': tipo})


def login_geral(request, tipo='aluno'):

    if request.method == 'POST':

        email = request.POST.get('email')
        senha_digitada = request.POST.get('senha')

        # 1. Tenta achar o usuário pelo e-mail
        usuario = Usuario.objects.filter(email=email).first()

        # 2. Verifica se o usuário existe E se a senha está correta
        if usuario and check_password(senha_digitada, usuario.senha):

            # 3. Salva o ID do usuário na sessão
            request.session['usuario_id'] = usuario.id

            # 4. Redireciona depois do login
            if tipo == 'professor':
                return redirect('primeiros_passos_professor')

            else:
                return redirect('primeiros_passos')

        else:

            # 5. Caso email ou senha estejam errados
            return render(request, 'usuarios/Login.html', {
                'error': 'E-mail ou senha incorretos.',
                'tipo': tipo
            })

    # 6. Se ele só abriu a página de login
    return render(request, 'usuarios/Login.html', {
        'tipo': tipo
    })


##Função para a página de primeiros passos do aluno
def primeiros_passos(request):
    return render(request, 'usuarios/Pagina_PrincipalAluno.html')


def perfil_aluno(request):
    return render(request, 'usuarios/perfil_aluno.html')


def primeiros_passos_professor(request):
    return render(request, 'usuarios/Pagina_PrincipalProf.html')

def cadastro_vaga(request):
    return render(request, 'usuarios/cadastro_vagas.html')