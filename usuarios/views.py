from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password, make_password
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.conf import settings
<<<<<<< HEAD
from django.db.models import Q

from .models import Usuario, Aluno, Professor, Vaga
=======
from .models import LinguagemProgramacao, TecnologiaFramework, AreaAtuacao
from usuarios.models import Usuario
from django.db.models import Q
from datetime import date
from django.db import transaction
from usuarios.models import Usuario, Vaga # Ferramenta nativa para criptografar
>>>>>>> tags-aluno
from .forms import CadastroInicialForm
from .models import Usuario, Aluno, Professor  # adiciona os dois no import
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def pagina_inicial(request):
    return render(request, 'usuarios/home.html')


<<<<<<< HEAD
=======


@transaction.atomic
>>>>>>> tags-aluno
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
<<<<<<< HEAD
=======
                # CORRIGIDO AQUI: de LoginAluno.html para Login.html
>>>>>>> tags-aluno
                return render(request, 'usuarios/Login.html', {
                    'error': 'Confirme seu e-mail antes de fazer login.'
                })

            request.session['usuario_id'] = usuario.id
            return redirect('primeiros_passos')

        else:
<<<<<<< HEAD
=======
            # CORRIGIDO AQUI TAMBÉM: de LoginAluno.html para Login.html
>>>>>>> tags-aluno
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

        # RESOLUÇÃO DO BUG: Se periodo_raw for um número válido, transforma em int. Se for vazio, vira None.
        periodo_raw = request.POST.get('periodo')
        periodo = int(periodo_raw) if periodo_raw and periodo_raw.isdigit() else None

        # 🛠️ CORREÇÃO: Criamos os dados padrão que SEMPRE serão atualizados
        defaults_dados = {
            'cpf': cpf,
            'matricula': matricula,
            'telefone': telefone,
            'curso': curso,
            'periodo': periodo,
            'sobre_voce': sobre,
        }

        # Só incluímos o currículo se um novo arquivo foi enviado.
        # Se veio vazio (None), o Django mantém o PDF antigo intacto no banco!
        if curriculo:
            defaults_dados['curriculo_pdf'] = curriculo 
            # 💡 Nota: Certifique-se de que o nome 'curriculo_pdf' está igualzinho no seu models.py!

        # Salvando ou atualizando no banco de dados
        aluno, created = Aluno.objects.update_or_create(
            dados_usuario=usuario,
            defaults=defaults_dados
        )

        # Atualizando ManyToMany das Linguagens
        lista_linguagens = request.POST.getlist('linguagens')
        if lista_linguagens:
            # 💡 Nota: Se o seu HTML enviar os IDs nos checkboxes, mude 'nome__in' para 'id__in'
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
<<<<<<< HEAD

    # CORREÇÃO: Removida a otimização select_related dos campos que não existem mais
    vagas = Vaga.objects.all()

=======
 
    vagas = Vaga.objects.all().order_by('-id')
 
>>>>>>> tags-aluno
    if q:
        # CORREÇÃO: Removido o filtro por "instituicao__nome_instituicao" que também geraria erro
        vagas = vagas.filter(
            Q(titulo__icontains=q) |
            Q(descricao__icontains=q) |
<<<<<<< HEAD
            Q(titulo__icontains=q) |
            Q(tipo_vaga__icontains=q)
=======
            Q(curso__icontains=q)
>>>>>>> tags-aluno
        )
 
    if tipo:
        vagas = vagas.filter(tipo_vaga=tipo)
 
    # IDs das vagas já salvas pelo aluno logado (para pintar a bandeirinha)
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
 
 
# ─────────────────────────────────────────────────────────────────────
# 3. Nova view salvar_vaga — adicione logo abaixo de lista_vagas:
# ─────────────────────────────────────────────────────────────────────
 
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
 
    # Toggle: se já salvou remove, se não salvou adiciona
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

<<<<<<< HEAD

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
=======
def cadastro_vaga(request):
    if request.method == 'POST':
        # 1. Captura os dados textuais simples do formulário
        titulo = request.POST.get('titulo')
        local = request.POST.get('local', '')
        carga_horaria = request.POST.get('carga_horaria', '')
        tipo_vaga = request.POST.get('tipo_vaga')
        descricao = request.POST.get('descricao', '')
        curso = request.POST.get('curso', '')
        periodo_minimo = request.POST.get('periodo_minimo', '')
        
        # 2. Captura o arquivo PDF anexado no dropzone do HTML
        anexo = request.FILES.get('anexo')

        # 3. Cria o registro da vaga no banco de dados (dados simples)
        vaga = Vaga.objects.create(
            titulo=titulo,
            local=local,
            carga_horaria=carga_horaria,
            tipo_vaga=tipo_vaga,
            descricao=descricao,
            curso=curso,
            periodo_minimo=periodo_minimo,
            anexo=anexo if anexo else None 
        )

        # 4. Captura as listas de IDs (o getlist junta todas as categorias automaticamente)
        ids_linguagens = request.POST.getlist('linguagens')
        ids_tecnologias = request.POST.getlist('tecnologias')
        ids_areas = request.POST.getlist('areas_atuacao')

        # 5. Vincula os IDs marcados às relações Muitos-para-Muitos
        if ids_linguagens:
            vaga.linguagens.set(ids_linguagens)
        if ids_tecnologias:
            vaga.tecnologias.set(ids_tecnologias)
        if ids_areas:
            vaga.areas_atuacao.set(ids_areas)

        # 6. Redireciona para a página de listagem de vagas geral do sistema
        return redirect('vagas')

    # ─────────────────────────────────────────────────────────────────
    # SE FOR ACESSO "GET" (Carregando a página pela primeira vez):
    # ─────────────────────────────────────────────────────────────────
    # Busca as opções padrão de linguagens e tecnologias
    linguagens = LinguagemProgramacao.objects.all().order_by('nome')
    tecnologias = TecnologiaFramework.objects.all().order_by('nome')

    # SEPARAÇÃO POR CATEGORIAS: Filtra as áreas de acordo com as etiquetas do model
    areas_informatica = AreaAtuacao.objects.filter(categoria='Informatica').order_by('nome')
    areas_exatas = AreaAtuacao.objects.filter(categoria='Exatas').order_by('nome')
    areas_engenharia = AreaAtuacao.objects.filter(categoria='Engenharia').order_by('nome')

    # Envia os grupos separados para o HTML renderizar cada um no seu devido bloco
    return render(request, 'usuarios/cadastro_vaga.html', {
        'linguagens': linguagens,
        'tecnologias': tecnologias,
        'areas_informatica': areas_informatica,
        'areas_exatas': areas_exatas,
        'areas_engenharia': areas_engenharia,
    })

>>>>>>> tags-aluno


def configuracoes(request):
    perfil = request.session.get('perfil_aluno', {})
    return render(request, 'usuarios/configuracoes.html', {'perfil': perfil})


def vagas_cadastradas(request):
    vagas = Vaga.objects.all().order_by('-criado_em')
    return render(request, 'usuarios/vagas_cadastradas.html', {'vagas': vagas})