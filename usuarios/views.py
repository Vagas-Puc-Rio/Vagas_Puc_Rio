from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password, make_password
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import date

from .models import (
    Usuario, Aluno, Professor,
    Vaga, LinguagemProgramacao, TecnologiaFramework, AreaAtuacao,
)
from .forms import CadastroInicialForm


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
                # Defaults provisórios para não quebrar os campos NOT NULL do model
                Aluno.objects.create(
                    dados_usuario=usuario,
                    data_nascimento=date(2000, 1, 1),
                    periodo=1,
                    tipo_interesse='',
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
        usuario_id = force_str(urlsafe_base64_decode(uid))
        email_esperado = force_str(urlsafe_base64_decode(token))

        usuario = Usuario.objects.get(pk=usuario_id, email=email_esperado)

        if usuario.ativo:
            return render(request, 'usuarios/confirmacao.html', {
                'mensagem': 'Sua conta já foi confirmada anteriormente. Faça login!'
            })

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
            if not usuario.ativo:
                return render(request, 'usuarios/Login.html', {
                    'error': 'Confirme seu e-mail antes de fazer login.'
                })

            request.session['usuario_id'] = usuario.id

            if tipo == 'professor':
                return redirect('primeiros_passos_professor')

            # Aluno: se já tem perfil preenchido, vai direto pra vagas.
            # Se não, vai pra primeiros-passos pra completar o cadastro.
            aluno = Aluno.objects.filter(dados_usuario=usuario).first()
            perfil_completo = bool(aluno and aluno.curso and aluno.matricula)

            if perfil_completo:
                return redirect('vagas')
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
        cpf = request.POST.get('cpf', '')
        matricula = request.POST.get('matricula', '')
        telefone = request.POST.get('telefone', '')  # ainda não existe no model, ver nota abaixo
        curso = request.POST.get('curso', '')
        sobre = request.POST.get('sobre', '')  # idem
        interesse = request.POST.get('interesse', '') or ', '.join(request.POST.getlist('tipo_vaga'))
        curriculo = request.FILES.get('curriculo')

        periodo_raw = request.POST.get('periodo')
        periodo = int(periodo_raw) if periodo_raw and periodo_raw.isdigit() else None

        defaults_dados = {
            'cpf': cpf,
            'matricula': matricula,
            'curso': curso,
            'periodo': periodo,
            'telefone': telefone,
            'sobre': sobre,
        }
        if curriculo:
            defaults_dados['curriculo'] = curriculo

        aluno, created = Aluno.objects.update_or_create(
            dados_usuario=usuario,
            defaults=defaults_dados,
        )

        lista_linguagens = request.POST.getlist('linguagens')
        if lista_linguagens:
            linguagens_db = LinguagemProgramacao.objects.filter(nome__in=lista_linguagens)
            aluno.linguagens.set(linguagens_db)

        lista_areas = request.POST.getlist('areas')
        if lista_areas:
            areas_db = AreaAtuacao.objects.filter(nome__in=lista_areas)
            aluno.areas_atuacao.set(areas_db)

        lista_tecnologias = request.POST.getlist('tecnologias')
        if lista_tecnologias:
            tecnologias_db = TecnologiaFramework.objects.filter(nome__in=lista_tecnologias)
            aluno.tecnologias.set(tecnologias_db)

        # Guardado na sessão pra tela de sucesso (inclui telefone/sobre que ainda não persistem no banco)
        request.session['perfil_aluno'] = {
            'nome': usuario.nome if usuario else 'Aluno',
            'email': usuario.email if usuario else '',
            'telefone': telefone,
            'matricula': matricula,
            'curso': curso,
            'periodo': periodo,
            'interesse': interesse,
            'linguagens': lista_linguagens,
            'tecnologias': lista_tecnologias,
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

    vagas = Vaga.objects.all().order_by('-id')

    if q:
        vagas = vagas.filter(
            Q(titulo__icontains=q) |
            Q(descricao__icontains=q) |
            Q(cursos__icontains=q) |
            Q(tipo_vaga__icontains=q)
        )

    if tipo:
        vagas = vagas.filter(tipo_vaga=tipo)

    usuario_id = request.session.get('usuario_id')
    vagas_salvas_ids = []
    if usuario_id:
        usuario = Usuario.objects.filter(id=usuario_id).first()
        aluno = Aluno.objects.filter(dados_usuario=usuario).first()
        if aluno:
            vagas_salvas_ids = list(aluno.vagas_salvas.values_list('id', flat=True))

    contexto = {
        'vagas': vagas,
        'total': vagas.count(),
        'q': q,
        'tipo_atual': tipo,
        'vagas_salvas_ids': vagas_salvas_ids,
    }
    return render(request, 'usuarios/lista_vagas.html', contexto)


def vaga_detalhe(request, vaga_id):
    vaga = Vaga.objects.filter(id=vaga_id).first()
    if not vaga:
        return redirect('vagas')

    dias_publicada = None
    if vaga.data_publicacao:
        dias_publicada = (date.today() - vaga.data_publicacao).days

    usuario_id = request.session.get('usuario_id')
    ja_salva = False
    if usuario_id:
        usuario = Usuario.objects.filter(id=usuario_id).first()
        aluno = Aluno.objects.filter(dados_usuario=usuario).first()
        if aluno:
            ja_salva = aluno.vagas_salvas.filter(id=vaga_id).exists()

    contexto = {
        'vaga': vaga,
        'dias_publicada': dias_publicada,
        'ja_salva': ja_salva,
        'beneficios': vaga.caracteristicas_set.all(),
        'tags': list(vaga.linguagens.all()) + list(vaga.tecnologias.all()) + list(vaga.areas_atuacao.all()),
    }
    return render(request, 'usuarios/vaga_detalhe.html', contexto)


@require_POST
def salvar_vaga(request, vaga_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return JsonResponse({'error': 'Não autenticado'}, status=401)

    usuario = Usuario.objects.filter(id=usuario_id).first()
    aluno = Aluno.objects.filter(dados_usuario=usuario).first()
    if not aluno:
        return JsonResponse({'error': 'Aluno não encontrado'}, status=404)

    vaga = Vaga.objects.filter(id=vaga_id).first()
    if not vaga:
        return JsonResponse({'error': 'Vaga não encontrada'}, status=404)

    if aluno.vagas_salvas.filter(id=vaga_id).exists():
        aluno.vagas_salvas.remove(vaga)
        salvo = False
    else:
        aluno.vagas_salvas.add(vaga)
        salvo = True

    return JsonResponse({'salvo': salvo})


def vagas_salvas(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.filter(id=usuario_id).first()
    aluno = Aluno.objects.filter(dados_usuario=usuario).first()
    vagas = aluno.vagas_salvas.all().order_by('-id') if aluno else []

    return render(request, 'usuarios/vagas_salvas.html', {
        'vagas': vagas
    })


def primeiros_passos_professor(request):
    return render(request, 'usuarios/Pagina_PrincipalProf.html')


def cadastro_vagas(request):
    if request.method == 'POST':
        vaga = Vaga.objects.create(
            titulo=request.POST.get('titulo'),
            local=request.POST.get('local', ''),
            carga_horaria=request.POST.get('carga_horaria', ''),
            tipo_vaga=request.POST.get('tipo_vaga') or ', '.join(request.POST.getlist('tipo_vaga')),
            modalidade=request.POST.get('modalidade', ''),
            salario=request.POST.get('salario', ''),
            data_publicacao=request.POST.get('data_publicacao') or None,
            prazo_candidatura=request.POST.get('prazo_candidatura') or None,
            descricao=request.POST.get('descricao', ''),
            cursos=request.POST.get('curso', '') or request.POST.get('cursos', ''),
            cr=request.POST.get('cr', ''),
            periodo_minimo=request.POST.get('periodo_minimo', ''),
            periodo_maximo=request.POST.get('periodo_maximo', ''),
            arquivo_vaga=request.FILES.get('arquivo_vaga') or request.FILES.get('anexo'),
        )

        ids_linguagens = request.POST.getlist('linguagens')
        ids_tecnologias = request.POST.getlist('tecnologias')
        ids_areas = request.POST.getlist('areas_atuacao') or request.POST.getlist('areas')

        if ids_linguagens:
            vaga.linguagens.set(ids_linguagens)
        if ids_tecnologias:
            vaga.tecnologias.set(ids_tecnologias)
        if ids_areas:
            vaga.areas_atuacao.set(ids_areas)

        return redirect('vagas_cadastradas')

    linguagens = LinguagemProgramacao.objects.all().order_by('nome')
    tecnologias = TecnologiaFramework.objects.all().order_by('nome')

    areas_informatica = AreaAtuacao.objects.filter(categoria='Informatica').order_by('nome')
    areas_exatas = AreaAtuacao.objects.filter(categoria='Exatas').order_by('nome')
    areas_engenharia = AreaAtuacao.objects.filter(categoria='Engenharia').order_by('nome')

    return render(request, 'usuarios/cadastro_vaga.html', {
        'linguagens': linguagens,
        'tecnologias': tecnologias,
        'areas_informatica': areas_informatica,
        'areas_exatas': areas_exatas,
        'areas_engenharia': areas_engenharia,
    })


def vagas_cadastradas(request):
    vagas = Vaga.objects.all().order_by('-criado_em')
    return render(request, 'usuarios/vagas_cadastradas.html', {'vagas': vagas})


def configuracoes(request):
    perfil = request.session.get('perfil_aluno', {})
    return render(request, 'usuarios/configuracoes.html', {'perfil': perfil})