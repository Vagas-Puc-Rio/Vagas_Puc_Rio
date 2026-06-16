from django.db import models

class Usuario(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=255)
    ativo = models.BooleanField(default=False) 

    def __str__(self):
        return self.nome

class Aluno(models.Model):
    dados_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    curso = models.CharField(max_length=100, null=True, blank=True)
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=30, null=True, blank=True)
    periodo = models.IntegerField(null=True, blank=True)

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
    titulo = models.CharField(max_length=200)
    local = models.CharField(max_length=200)
    carga_horaria = models.CharField(max_length=100, blank=True)
    tipo_vaga = models.CharField(max_length=100)
    modalidade = models.CharField(max_length=100, blank=True)
    salario = models.CharField(max_length=100, blank=True)
    data_publicacao = models.DateField(null=True, blank=True)
    prazo_candidatura = models.DateField(null=True, blank=True)
    descricao = models.TextField(blank=True)
    cursos = models.CharField(max_length=200, blank=True)
    cr = models.CharField(max_length=20, blank=True)
    periodo_minimo = models.CharField(max_length=50, blank=True)
    periodo_maximo = models.CharField(max_length=50, blank=True)
    arquivo_vaga = models.FileField(upload_to='vagas/', null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
    
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

