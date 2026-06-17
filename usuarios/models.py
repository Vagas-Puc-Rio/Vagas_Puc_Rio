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
    # Definimos as grandes categorias que aparecem no Figma
    CATEGORIAS_CHOICES = [
        ('Informatica', 'Informática'),
        ('Exatas', 'Exatas'),
        ('Engenharia', 'Engenharia'),
    ]
    
    nome = models.CharField(max_length=100, unique=True)
    # Adiciona a etiqueta da categoria com um valor padrão para não quebrar dados antigos
    categoria = models.CharField(max_length=50, choices=CATEGORIAS_CHOICES, default='Informatica')

    def __str__(self):
        return f"[{self.categoria}] {self.nome}"
    
class TecnologiaFramework(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.nome

class Aluno(models.Model):
    dados_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=20, unique=True)
    curso = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=30)
    periodo = models.IntegerField()
    curriculo = models.FileField(upload_to='alunos/curriculos/', blank=True, null=True)
    vagas_salvas = models.ManyToManyField("Vaga", blank=True, related_name='alunos_favoritaram')
    
    TIPOS_INTERESSE = [
        ('estagio', 'Estágio'),
        ('ic', 'Iniciação Científica (IC)'),
        ('ambos', 'Ambos'),
    ]
    tipo_interesse = models.CharField(max_length=20, choices=TIPOS_INTERESSE, null=True)

    # 2. MÚLTIPLA ESCOLHA: As Tags (ManyToManyField)
    # O blank=True permite que o aluno deixe vazio caso não saiba nenhuma ainda
    linguagens = models.ManyToManyField(LinguagemProgramacao, blank=True)
    areas_atuacao = models.ManyToManyField(AreaAtuacao, blank=True)
    tecnologias = models.ManyToManyField(TecnologiaFramework, blank=True)

    def __str__(self):
        return self.dados_usuario.nome
    

    
class Professor(models.Model):
    dados_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    disciplina = models.CharField(max_length=100, null=True, blank=True)  # adiciona null e blank
    departamento = models.CharField(max_length=100, null=True, blank=True)
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
    # Campos simples de texto e arquivo que a View está tentando salvar
    titulo = models.CharField(max_length=255)
    local = models.CharField(max_length=255, blank=True, null=True)
    carga_horaria = models.CharField(max_length=100, blank=True, null=True)
    tipo_vaga = models.CharField(max_length=50) # Estágio ou Iniciação Científica
    descricao = models.TextField(blank=True, null=True)
    curso = models.CharField(max_length=255, blank=True, null=True)
    periodo_minimo = models.CharField(max_length=50, blank=True, null=True)
    anexo = models.FileField(upload_to='vagas/anexos/', blank=True, null=True)

    # Relacionamentos Muitos-para-Muitos das etapas 4, 5 e 6
    linguagens = models.ManyToManyField(LinguagemProgramacao, blank=True)
    tecnologias = models.ManyToManyField(TecnologiaFramework, blank=True)
    areas_atuacao = models.ManyToManyField(AreaAtuacao, blank=True)

    def __str__(self):
        return self.titulo # Retorna os primeiros 50 caracteres da descrição para facilitar a visualização
    
    def match_de_vagas(self,aluno):
        #Ai aqui verifica o perido da vaga e o periodo do aluno, mais pra frente teremos q implementar os outros requisitos
        if aluno.periodo >= self.periodo_min:
            return True
        else:
            return False

##class Bolsa(models.Model):
    ##vagas = models.OneToOneField(Vaga, on_delete = models.CASCADE)

    ##salario = models.DecimalField(max_digits=10, decimal_places=2 , null=True, blank=True)

    ##carga_horaria = models.IntegerField()

    ##def possui_salario(self):
        ##if self.salario:
            ##return True
        ##else:
            ##return False
    
    ##def __str__(self):
        ##if self.salario:
            ##return f"Bolsa remunerada - {self.vaga} - R$ {self.salario}"
        ##else:
            ##return f"Bolsa não remunerada - {self.vaga}"
        
##class Estagio(models.Model):
    ##vaga = models.OneToOneField(Vaga, on_delete=models.CASCADE)
    ##salario = models.DecimalField(max_digits=10, decimal_places=2)
    ##carga_horaria = models.IntegerField()
    
    ##def __str__(self):
        ##return f"Estágio - {self.vaga} - R$ {self.salario}"
    
class Caracteristicas(models.Model):
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE)
    auxilios = models.TextField(blank=True, null=True)
    titulo = models.CharField(max_length=200)
    tipo_vaga = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ##def match_de_vagas(self,aluno):
        #Ai aqui verifica o perido da vaga e o periodo do aluno, mais pra frente teremos q implementar os outros requisitos
        ##if aluno.periodo >= self.periodo_min:
            ##return True
        ####return False

    def __str__(self):
        return self.titulo

