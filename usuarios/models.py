from django.db import models

class Usuario(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=255)

    def __str__(self):
        return self.nome

class Aluno(models.Model):
    dados_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=20, unique=True)
    curso = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    genero = models.CharField(max_length=30)
    periodo = models.IntegerField()

    def __str__(self):
        return self.dados_usuario.nome
    
class Professor(models.Model):
    dados_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    disciplina = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100, blank=True, null=True)

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
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)

    descricao = models.TextField()
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    beneficios = models.TextField(blank=True, null=True)
    carga_horaria = models.IntegerField(null=True, blank=True)
    periodo_min = models.IntegerField(null=True, blank=True)
    tipo_vaga = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.descricao[:50]  # Retorna os primeiros 50 caracteres da descrição para facilitar a visualização
    
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

