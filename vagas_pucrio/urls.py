"""
URL configuration for vagas_pucrio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from usuarios import views

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

    path('primeiros-passos-professor/',views.primeiros_passos_professor,
         name='primeiros_passos_professor'),

    path('cadastro-vaga/', views.cadastro_vaga,
         name='cadastro_vaga'),

    path('vagas/', views.lista_vagas, name='vagas'),

    path('perfil/aluno/pronto/', views.perfil_alunopronta, name='perfil_alunopronta'),

    path('configuracoes/', views.configuracoes, name='configuracoes'),
]
