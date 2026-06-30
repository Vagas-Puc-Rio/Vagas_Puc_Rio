from datetime import date
from django.db import models


class Usuario(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=255)
    ativo = models.BooleanField(default=False)

    def __str__(self):
        return self.nome


class LinguagemProgramacao(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome


class AreaAtuacao(models.Model):
    CATEGORIAS_CHOICES = [
        ('Informatica', 'Informática'),
        ('Exatas', 'Exatas'),
        ('Engenharia', 'Engenharia'),
    ]

    nome = models.CharField(max_length=100, unique=True)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS_CHOICES, default='Informatica')

    def __str__(self):
        return f"[{self.categoria}] {self.nome}"


class TecnologiaFramework(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome


class Curso(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class Aluno(models.Model):
    dados_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    curso = models.ForeignKey(Curso, null=True, blank=True, on_delete=models.SET_NULL, related_name='alunos')
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    cr = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=30, blank=True)
    periodo = models.IntegerField(null=True, blank=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    sobre = models.TextField(blank=True, null=True)
    curriculo = models.FileField(upload_to='alunos/curriculos/', blank=True, null=True)
    vagas_salvas = models.ManyToManyField("Vaga", blank=True, related_name='alunos_favoritaram')

    TIPOS_INTERESSE = [
        ('estagio', 'Estágio'),
        ('ic', 'Iniciação Científica (IC)'),
        ('ambos', 'Ambos'),
    ]
    tipo_interesse = models.CharField(max_length=20, choices=TIPOS_INTERESSE, null=True)

    linguagens = models.ManyToManyField(LinguagemProgramacao, blank=True)
    areas_atuacao = models.ManyToManyField(AreaAtuacao, blank=True)
    tecnologias = models.ManyToManyField(TecnologiaFramework, blank=True)

    def __str__(self):
        return self.dados_usuario.nome


class Professor(models.Model):
    dados_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    codigo_identificacao = models.CharField(max_length=50, blank=True, null=True)
    departamento = models.CharField(max_length=100, null=True, blank=True)
    disciplina = models.CharField(max_length=255, blank=True, null=True)  # disciplinas separadas por vírgula
    sobre = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.dados_usuario.nome


class Funcionario(models.Model):
    dados_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.dados_usuario.nome


class Instituicao(models.Model):
    nome_instituicao = models.CharField(max_length=255)
    endereco = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18, unique=True)

    def __str__(self):
        return self.nome_instituicao


class Vaga(models.Model):
    VAGAS_CHOICES = [
        ('Estágio', 'Estágio'),
        ('Iniciação Científica', 'Iniciação Científica (IC)'),
        ('Trainee', 'Trainee'),
    ]

    MODALIDADE_CHOICES = [
        ('Presencial', 'Presencial'),
        ('Híbrido', 'Híbrido'),
        ('Remoto', 'Remoto'),
    ]

    titulo = models.CharField(max_length=200)

    # MUDADO DE VOLTA PARA TEXTO LIVRE: Qualquer empresa digita o endereço que quiser
    local = models.CharField(max_length=255, blank=True, null=True)

    carga_horaria = models.CharField(max_length=100, blank=True, null=True)
    tipo_vaga = models.CharField(max_length=50, choices=VAGAS_CHOICES, default='Estágio')
    modalidade = models.CharField(max_length=50, choices=MODALIDADE_CHOICES, default='Presencial')
    salario = models.CharField(max_length=100, blank=True)
    data_publicacao = models.DateField(null=True, blank=True)
    prazo_candidatura = models.DateField(null=True, blank=True)
    descricao = models.TextField(blank=True, null=True)
    cursos = models.ManyToManyField(Curso, blank=True, related_name='vagas')
    cr = models.CharField(max_length=20, blank=True)
    periodo_minimo = models.IntegerField(blank=True, null=True)
    periodo_maximo = models.IntegerField(blank=True, null=True)
    arquivo_vaga = models.FileField(upload_to='vagas/', blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    professor_responsavel = models.ForeignKey(
        Professor, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='vagas_publicadas'
    )

    linguagens = models.ManyToManyField(LinguagemProgramacao, blank=True)
    tecnologias = models.ManyToManyField(TecnologiaFramework, blank=True)
    areas_atuacao = models.ManyToManyField(AreaAtuacao, blank=True)

    def __str__(self):
        return self.titulo

    @property
    def status(self):
        if self.prazo_candidatura and self.prazo_candidatura < date.today():
            return 'Finalizada'
        return 'Disponível'

    def match_de_vagas(self, aluno):
        if self.periodo_minimo is None:
            return True
        return aluno.periodo >= self.periodo_minimo

    def calcular_detalhes_match(self, aluno):
        """
        Retorna a porcentagem de match e as competências que combinam ou faltam.
        Ideal para renderizar a tela de vagas recomendadas.
        """
        # 1. Filtros Eliminatórios (Curso e Período)
        if self.cursos.exists() and aluno.curso not in self.cursos.all():
            return {"porcentagem": 0, "combinam": [], "faltam": [], "valido": False}

        if self.periodo_minimo and (aluno.periodo or 0) < self.periodo_minimo:
            return {"porcentagem": 0, "combinam": [], "faltam": [], "valido": False}

        if self.periodo_maximo and (aluno.periodo or 0) > self.periodo_maximo:
            return {"porcentagem": 0, "combinam": [], "faltam": [], "valido": False}

        # 2. Levantamento de Requisitos da Vaga vs Competências do Aluno
        vaga_linguagens = set(self.linguagens.all())
        vaga_tecnologias = set(self.tecnologias.all())
        vaga_areas = set(self.areas_atuacao.all())

        aluno_linguagens = set(aluno.linguagens.all())
        aluno_tecnologias = set(aluno.tecnologias.all())
        aluno_areas = set(aluno.areas_atuacao.all())

        todos_requisitos_vaga = vaga_linguagens.union(vaga_tecnologias).union(vaga_areas)

        combinam = []
        faltam = []

        if not todos_requisitos_vaga:
            return {"porcentagem": 100, "combinam": [], "faltam": [], "valido": True}

        for lang in vaga_linguagens:
            if lang in aluno_linguagens:
                combinam.append({"nome": lang.nome, "status": "combina"})
            else:
                faltam.append({"nome": lang.nome, "status": "falta"})

        for tec in vaga_tecnologias:
            if tec in aluno_tecnologias:
                combinam.append({"nome": tec.nome, "status": "combina"})
            else:
                faltam.append({"nome": tec.nome, "status": "falta"})

        for area in vaga_areas:
            if area in aluno_areas:
                combinam.append({"nome": area.nome, "status": "combina"})
            else:
                faltam.append({"nome": area.nome, "status": "falta"})

        total_requisitos = len(todos_requisitos_vaga)
        total_atendidos = len(combinam)
        porcentagem = int((total_atendidos / total_requisitos) * 100)

        return {
            "porcentagem": porcentagem,
            "combinam": combinam,
            "faltam": faltam,
            "valido": True,
        }


class Caracteristicas(models.Model):
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE)
    auxilios = models.TextField(blank=True, null=True)
    titulo = models.CharField(max_length=200)
    tipo_vaga = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.titulo