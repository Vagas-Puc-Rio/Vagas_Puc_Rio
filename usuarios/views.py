from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password, make_password
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q

from .models import Usuario, Aluno, Professor, Vaga
from .forms import CadastroInicialForm


def pagina_inicial(request):
    return render(request, 'usuarios/home.html')


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
                # Se você configurou no settings.py para printar no console, 
                # o e-mail aparecerá direto no terminal do seu VS Code!
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


def login_geral(request, tipo='aluno'):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha_digitada = request.POST.get('senha')

        usuario = Usuario.objects.filter(email=email).first()

        if usuario and check_password(senha_digitada, usuario.senha):
            # Bloqueia login se ainda não confirmou o e-mail
            if not usuario.ativo:
                return render(request, 'usuarios/Login.html', {
                    'error': 'Confirme seu e-mail antes de fazer login.' 
                })

            request.session['usuario_id'] = usuario.id
            return redirect('primeiros_passos')

        else:
            return render(request, 'usuarios/Login.html', {
                'error': 'E-mail ou senha incorretos.'
            })

    return render(request, 'usuarios/Login.html')


def primeiros_passos(request):
    return render(request, 'usuarios/Pagina_PrincipalAluno.html')


def perfil_aluno(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.filter(id=usuario_id).first()

    if request.method == 'POST':
        request.session['perfil_aluno'] = {
            'nome': request.POST.get('nome') or request.POST.get('nome_completo'),
            'email': usuario.email if usuario else '',
            'telefone': request.POST.get('telefone'),
            'matricula': request.POST.get('matricula'),
            'periodo': request.POST.get('periodo'),
            'curso': request.POST.get('curso'),
            'interesse': request.POST.getlist('interesse') or request.POST.getlist('tipo_vaga'),
            'linguagens': request.POST.getlist('linguagens'),
            'tecnologias': request.POST.getlist('tecnologias'),
            'areas': request.POST.getlist('areas'),
            'softskills': request.POST.getlist('softskills'),
            'idiomas': request.POST.getlist('idiomas'),
            'sobre': request.POST.get('sobre'),
        }

        return redirect('perfil_alunopronta')

    return render(request, 'usuarios/perfil_aluno.html')


def perfil_alunopronta(request):
    perfil = request.session.get('perfil_aluno', {})
    return render(request, 'usuarios/perfil_alunopronta.html', {'perfil': perfil})


def lista_vagas(request):
    q = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '').strip()

    # CORREÇÃO: Removida a otimização select_related dos campos que não existem mais
    vagas = Vaga.objects.all()

    if q:
        # CORREÇÃO: Removido o filtro por "instituicao__nome_instituicao" que também geraria erro
        vagas = vagas.filter(
            Q(descricao__icontains=q) |
            Q(titulo__icontains=q) |
            Q(tipo_vaga__icontains=q)
        )
    if tipo:
        vagas = vagas.filter(tipo_vaga=tipo)

    contexto = {
        'vagas': vagas,
        'total': vagas.count(),
        'q': q,
        'tipo_atual': tipo,
    }
    return render(request, 'usuarios/lista_vagas.html', contexto)


def primeiros_passos_professor(request):
    return render(request, 'usuarios/Pagina_PrincipalProf.html')


def cadastro_vagas(request):
    if request.method == 'POST':
        vaga = Vaga(
            titulo=request.POST.get('titulo'),
            local=request.POST.get('local'),
            carga_horaria=request.POST.get('carga_horaria'),
            tipo_vaga=', '.join(request.POST.getlist('tipo_vaga')),
            modalidade=request.POST.get('modalidade'),
            salario=request.POST.get('salario'),
            data_publicacao=request.POST.get('data_publicacao') or None,
            prazo_candidatura=request.POST.get('prazo_candidatura') or None,
            descricao=request.POST.get('descricao'),
            cursos=request.POST.get('cursos'),
            cr=request.POST.get('cr'),
            periodo_minimo=request.POST.get('periodo_minimo'),
            periodo_maximo=request.POST.get('periodo_maximo'),
            arquivo_vaga=request.FILES.get('arquivo_vaga')
        )
        vaga.save()
        return redirect('vagas_cadastradas')

    return render(request, 'usuarios/cadastro_vagas.html')


def configuracoes(request):
    perfil = request.session.get('perfil_aluno', {})
    return render(request, 'usuarios/configuracoes.html', {'perfil': perfil})


def vagas_cadastradas(request):
    vagas = Vaga.objects.all().order_by('-criado_em')
    return render(request, 'usuarios/vagas_cadastradas.html', {'vagas': vagas})