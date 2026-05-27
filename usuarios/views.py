from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password, make_password
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User  # necessário para o token
from django.conf import settings

from usuarios.models import Usuario
from .forms import CadastroInicialForm


def pagina_inicial(request):
    return render(request, 'usuarios/home.html')


from .models import Usuario, Aluno, Professor  # adiciona os dois no import

def cadastro_inicial(request, tipo):
    if request.method == 'POST':
        form = CadastroInicialForm(request.POST)

        if form.is_valid():
            usuario = form.save(commit=False)
            senha_pura = form.cleaned_data['senha']
            usuario.senha = make_password(senha_pura)
            usuario.ativo = False
            usuario.save()

            # Cria Aluno ou Professor dependendo do tipo
            if tipo == 'aluno':
                Aluno.objects.create(dados_usuario=usuario)
            elif tipo == 'professor':
                Professor.objects.create(dados_usuario=usuario)

            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            token = urlsafe_base64_encode(force_bytes(usuario.email))

            dominio = request.build_absolute_uri('/')[:-1]
            link = f"{dominio}/confirmar-email/{uid}/{token}/"

            send_mail(
                subject='Confirme seu cadastro - Vagas PUC-Rio',
                message=f'Olá, {usuario.nome}!\n\nClique no link abaixo para ativar sua conta:\n\n{link}\n\nSe você não se cadastrou, ignore este e-mail.',
                from_email='noreplyvagaspucrio@gmail.com',
                recipient_list=[usuario.email],
                fail_silently=False,
            )

            return render(request, 'usuarios/email_enviado.html', {'email': usuario.email})

    else:
        form = CadastroInicialForm()

    return render(request, 'usuarios/cadastro_inicial.html', {'form': form, 'tipo': tipo})

def confirmar_email(request, uid, token):
    try:
        # Decodifica o uid para pegar o ID do usuário
        usuario_id = force_str(urlsafe_base64_decode(uid))
        email_esperado = force_str(urlsafe_base64_decode(token))

        usuario = Usuario.objects.get(pk=usuario_id, email=email_esperado)

        if usuario.ativo:
            return render(request, 'usuarios/confirmacao.html', {
                'mensagem': 'Sua conta já foi confirmada anteriormente. Faça login!'
            })

        # Ativa a conta
        usuario.ativo = True
        usuario.save()

        return render(request, 'usuarios/confirmacao.html', {
            'mensagem': 'E-mail confirmado com sucesso! Agora você pode fazer login.'
        })

    except (Usuario.DoesNotExist, Exception):
        return render(request, 'usuarios/confirmacao.html', {
            'mensagem': 'Link inválido ou expirado. Tente se cadastrar novamente.'
        })


def login_geral(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha_digitada = request.POST.get('senha')

        usuario = Usuario.objects.filter(email=email).first()

        if usuario and check_password(senha_digitada, usuario.senha):

            # Bloqueia login se ainda não confirmou o e-mail
            if not usuario.ativo:
                return render(request, 'usuarios/LoginAluno.html', {
                    'error': 'Confirme seu e-mail antes de fazer login.'
                })

            request.session['usuario_id'] = usuario.id
            return redirect('primeiros_passos')

        else:
            return render(request, 'usuarios/LoginAluno.html', {
                'error': 'E-mail ou senha incorretos.'
            })

    return render(request, 'usuarios/LoginAluno.html')


def primeiros_passos(request):
    return render(request, 'usuarios/Pagina_PrincipalAluno.html')