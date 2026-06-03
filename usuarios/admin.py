from django.contrib import admin
from .models import *


admin.site.register(Usuario)
admin.site.register(Aluno)
admin.site.register(Professor)
admin.site.register(Funcionario)
admin.site.register(Instituicao)
admin.site.register(Vaga)

admin.site.register(Caracteristicas)
admin.site.register(LinguagemProgramacao)
admin.site.register(AreaAtuacao)
##admin.site.register(Bolsa)
##admin.site.register(Estagio)


