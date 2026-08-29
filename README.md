# Vagas PUC-Rio

Este repositório contém o código-fonte e a documentação do projeto desenvolvido em conjunto para as disciplinas de **Projetos Interativos** e **Interação Humano-Computador (IHC)** da PUC-Rio. 

O objetivo principal da aplicação é solucionar a falta de centralização de informações sobre vagas de estágio e Iniciação Científica (IC) dentro da universidade, conectando alunos, professores e empresas em uma única plataforma.

## Objetivo e Contexto

O desenvolvimento do projeto envolveu um ciclo completo de Design e pesquisa, englobando:
* **Pesquisa e Entrevistas:** Levantamento de requisitos e dores reais dos alunos e professores da PUC-Rio.
* **Design e Prototipação:** Criação de interfaces no Figma, além de avaliações heurísticas e testes de usabilidade.
* **Desenvolvimento Web:** Implementação do back-end e integração de banco de dados utilizando Python e Django.

## Tecnologias Utilizadas

* **Back-end e Framework:** Python, Django
* **Banco de Dados:** Gerenciado nativamente pelo ORM do Django
* **Design de Interface:** Figma

## Perfis de Usuário e Status de Implementação

O sistema foi modelado para atender três tipos principais de usuários, com os seguintes status de desenvolvimento no protótipo atual:

| Perfil | Descrição e Permissões | Status |
| :--- | :--- | :--- |
| **Aluno** | Visualiza as oportunidades disponíveis (estágio e IC), busca vagas e gerencia seu perfil. | **Implementado** |
| **Professor** | Divulga oportunidades de Iniciação Científica e gerencia as candidaturas dos alunos. |**Parcialmente Implementado** |
| **Colaborador (Empresa)** | Representante externo que solicita o registro da empresa para postar vagas de estágio. | **Não Implementado (Trabalho Futuro)** |

## Como Executar o Projeto Localmente

Para rodar o projeto na sua máquina para testes ou desenvolvimento, siga os passos abaixo:

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/vagas-puc-rio.git
cd vagas-puc-rio
```

**2. Crie e ative um ambiente virtual (recomendado)**
```bash
python -m venv venv
# No Windows: venv\Scripts\activate
# No Linux/Mac: source venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install django
```

**4. Realize as migrações do Banco de Dados**
```bash
python manage.py makemigrations
python manage.py migrate
```

**5. Inicie o servidor de desenvolvimento**
```bash
python manage.py runserver
```

Acesse a aplicação no seu navegador através do endereço `http://127.0.0.1:8000/`.

---

Para criar um usuário administrador e acessar o painel do Django (`/admin`), utilize o comando:
```bash
python manage.py createsuperuser
```
