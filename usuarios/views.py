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
                return redirect('completar_perfil_aluno', usuario_id=usuario.id)
            else:
                # Manda para a URL de completar perfil do professor
                return redirect('completar_perfil_professor', usuario_id=usuario.id)
    else:
        form = CadastroInicialForm()
        
    return render(request, 'usuarios/cadastro_inicial.html', {'form': form, 'tipo': tipo})


def login_geral(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha_digitada = request.POST.get('senha')
        
        # 1. Tenta achar o usuário pelo e-mail
        usuario = Usuario.objects.filter(email=email).first()
        
        # 2. Se o usuário existir E a senha digitada bater com a criptografada no banco
        if usuario and check_password(senha_digitada, usuario.senha):
            
            # 3. O "Pulo do Gato": Salva o ID dele na sessão (Isso é o que mantém ele logado!)
            request.session['usuario_id'] = usuario.id
            
            # 4. A sua lógica excelente para descobrir quem é quem
            if hasattr(usuario, 'aluno'):
                return redirect('dashboard_aluno')
            elif hasattr(usuario, 'professor'):
                return redirect('dashboard_professor')
            else:
                # Cai aqui se ele fez o cadastro inicial, mas não completou o perfil ainda
                return render(request, 'usuarios/login.html', {'error': 'Termine seu cadastro primeiro.'})
                
        else:
            # Mensagem genérica por segurança (não diga se o erro foi no email ou na senha)
            return render(request, 'usuarios/login.html', {'error': 'E-mail ou senha inválidos.'})
            
    # Se ele só acessou a página (GET), mostra o formulário vazio
    return render(request, 'usuarios/login.html')