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
    path('cadastro/aluno/', views.cadastro_inicial, name='cadastro_aluno'),
    path('login/', views.login_geral, name='login'),
    path('primeiros-passos/', views.primeiros_passos, name='primeiros_passos'),
    path('perfil-aluno/', views.perfil_aluno, name='perfil_aluno'),
]
