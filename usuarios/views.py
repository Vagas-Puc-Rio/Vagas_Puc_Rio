from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password, make_password
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User  # necessário para o token
from django.conf import settings
from .models import Usuario, Aluno, LinguagemProgramacao, AreaAtuacao
from usuarios.models import Usuario
from django.db.models import Q
from datetime import date
from django.db import transaction
from usuarios.models import Usuario, Vaga # Ferramenta nativa para criptografar
from .forms import CadastroInicialForm
from .models import Usuario, Aluno, Professor  # adiciona os dois no import

def pagina_inicial(request):
    return render(request, 'usuarios/home.html')




@transaction.atomic
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
                # Alimentando todos os campos estritos com defaults provisórios
                Aluno.objects.create(
                    dados_usuario=usuario, 
                    data_nascimento=date(2000, 1, 1),
                    periodo=1,             # Evita o erro atual de NOT NULL
                    tipo_interesse=''      # Protege contra o próximo possível erro
                )
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


def login_geral(request, tipo='aluno'):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha_digitada = request.POST.get('senha')

        usuario = Usuario.objects.filter(email=email).first()

        if usuario and check_password(senha_digitada, usuario.senha):
            # Bloqueia login se ainda não confirmou o e-mail
            if not usuario.ativo:
                # CORRIGIDO AQUI: de LoginAluno.html para Login.html
                return render(request, 'usuarios/Login.html', {
                    'error': 'Confirme seu e-mail antes de fazer login.'
                })

            request.session['usuario_id'] = usuario.id
            return redirect('primeiros_passos')

        else:
            # CORRIGIDO AQUI TAMBÉM: de LoginAluno.html para Login.html
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
        cpf = request.POST.get('cpf', '')
        matricula = request.POST.get('matricula', '')
        telefone = request.POST.get('telefone', '')
        curso = request.POST.get('curso', '')
        sobre = request.POST.get('sobre', '')
        interesse = request.POST.get('interesse', '') # Captura o tipo de vaga (Estágio/IC)
        curriculo = request.FILES.get('curriculo')

        # 1. Recupera o período bruto enviado pelo formulário
        periodo_raw = request.POST.get('periodo', '')

        # 2. Busca se o aluno já tem um registro salvo no banco
        aluno_existente = Aluno.objects.filter(dados_usuario=usuario).first()

        # 3. BLINDAGEM CONTRA NULL: Decide o período sem deixar brecha para None
        if periodo_raw and str(periodo_raw).isdigit():
            periodo_final = int(periodo_raw)
        else:
            # Se veio vazio, tenta manter o que já estava no banco. Se não tiver nada, assume 1.
            periodo_final = aluno_existente.periodo if aluno_existente else 1

        # 4. Monta o dicionário de atualização garantindo que o período é um número válido
        model_defaults = {
            'cpf': cpf,
            'matricula': matricula,
            'telefone': telefone,
            'curso': curso,
            'sobre_voce': sobre,
            'periodo': periodo_final, # Proteção total aplicada aqui
            'tipo_interesse': interesse,
        }

        # Atualiza o arquivo de currículo apenas se um novo foi enviado
        if curriculo:
            model_defaults['curriculo_pdf'] = curriculo

        # Salva com segurança no SQLite
        aluno, created = Aluno.objects.update_or_create(
            dados_usuario=usuario,
            defaults=model_defaults
        )

        # Atualizando ManyToMany das Linguagens
        lista_linguagens = request.POST.getlist('linguagens')
        if lista_linguagens:
            linguagens_db = LinguagemProgramacao.objects.filter(nome__in=lista_linguagens)
            aluno.linguagens.set(linguagens_db)

        # Atualizando ManyToMany das Áreas
        lista_areas = request.POST.getlist('areas')
        if lista_areas:
            areas_db = AreaAtuacao.objects.filter(nome__in=lista_areas)
            aluno.areas_atuacao.set(areas_db)

        # Atualiza os dados da sessão para a tela de sucesso
        request.session['perfil_aluno'] = {
            'nome': usuario.nome if usuario else 'Aluno',
            'email': usuario.email if usuario else '',
            'telefone': telefone,
            'matricula': matricula,
            'curso': curso,
            'periodo': periodo_final,
            'interesse': interesse,
            'linguagens': lista_linguagens,
            'areas': lista_areas,
            'sobre': sobre,
        }

        return redirect('perfil_alunopronta')

    return render(request, 'usuarios/perfil_aluno.html')


def perfil_alunopronta(request):
    perfil = request.session.get('perfil_aluno', {})
    return render(request, 'usuarios/perfil_alunopronta.html', {'perfil': perfil})

def lista_vagas(request):
    q = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '').strip()

    vagas = Vaga.objects.select_related(
        'instituicao', 'professor', 'professor__dados_usuario'
    ).all()

    if q:
        vagas = vagas.filter(
            Q(descricao__icontains=q) |
            Q(instituicao__nome_instituicao__icontains=q) |
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

def cadastro_vaga(request):
    return render(request, 'usuarios/cadastro_vagas.html')

def configuracoes(request):
    perfil = request.session.get('perfil_aluno', {})
    return render(request, 'usuarios/configuracoes.html', {'perfil': perfil})