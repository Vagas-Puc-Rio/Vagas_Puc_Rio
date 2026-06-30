from django.contrib import admin
from django.urls import path
from usuarios import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.pagina_inicial, name='home'),

    path('cadastro/<str:tipo>/', views.cadastro_inicial, name='cadastro'),

    path('cadastro/aluno/', views.cadastro_inicial,
         {'tipo': 'aluno'}, name='cadastro_aluno'),

    path('cadastro/professor/', views.cadastro_inicial,
         {'tipo': 'professor'}, name='cadastro_professor'),

    path('login/aluno/', views.login_geral,
         {'tipo': 'aluno'}, name='login_aluno'),

    path('login/professor/', views.login_geral,
         {'tipo': 'professor'}, name='login_professor'),

    path('primeiros-passos/', views.primeiros_passos,
         name='primeiros_passos'),

    path('confirmar-email/<str:uid>/<str:token>/', views.confirmar_email, name='confirmar_email'),

    path('perfil-aluno/', views.perfil_aluno,
         name='perfil_aluno'),

    path('primeiros-passos-professor/', views.primeiros_passos_professor,
         name='primeiros_passos_professor'),

    path('cadastro-vagas/', views.cadastro_vagas, name='cadastro_vagas'),

    path('vagas/', views.lista_vagas, name='vagas'),
    path('vagas/recomendadas/', views.vagas_recomendadas, name='vagas_recomendadas'),
    path('vagas/salvar/<int:vaga_id>/', views.salvar_vaga, name='salvar_vaga'),
    path('vagas/<int:vaga_id>/', views.vaga_detalhe, name='vaga_detalhe'),

    path('vagas_salvas/', views.vagas_salvas, name='vagas_salvas'),
    path('perfil/aluno/pronto/', views.perfil_alunopronta, name='perfil_alunopronta'),

    path('perfil-professor/', views.perfil_professor, name='perfil_professor'),
    path('perfil-professor/pronto/', views.perfil_professorpronto, name='perfil_professorpronto'),

    path('configuracoes/', views.configuracoes, name='configuracoes'),

    path('vagas-cadastradas/', views.vagas_cadastradas, name='vagas_cadastradas'),
    path('vagas-cadastradas/editar/<int:vaga_id>/', views.editar_vaga, name='editar_vaga'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)