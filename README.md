# Vagas PUC-Rio

Plataforma web para centralizar oportunidades de **estágio** e **Iniciação Científica (IC)** na PUC-Rio, conectando alunos, professores e empresas em um único lugar. Desenvolvido para as disciplinas de Projetos Interativos e Interação Humano-Computador (IHC).

## Funcionalidades técnicas implementadas

- **Algoritmo de matching aluno–vaga**: cálculo de compatibilidade entre o perfil do aluno e as vagas disponíveis (`calcular_detalhes_match`), usado na página de vagas recomendadas
- **Página de vagas recomendadas** com visualização de compatibilidade
- **Sistema de favoritos**: alunos podem salvar/marcar vagas de interesse
- **Autenticação customizada** com fluxo de confirmação de cadastro por email (SMTP via Gmail, credenciais gerenciadas com `.env`)
- **Painel administrativo** customizado no Django Admin
- **Modelagem de dados**: modelo `Curso` e estrutura relacional para vagas, alunos e candidaturas

## Tecnologias

- **Back-end**: Python, Django
- **Banco de dados**: gerenciado nativamente via ORM do Django
- **Front-end**: templates Django (HTML/CSS a partir de protótipos do Figma)
- **Autenticação/Email**: Django Auth + SMTP (Gmail)

## Contexto do projeto

Além da implementação, o projeto passou por um ciclo de design e pesquisa:

- **Pesquisa e entrevistas**: levantamento de requisitos com alunos e professores da PUC-Rio
- **Prototipação**: interfaces no Figma, avaliações heurísticas e testes de usabilidade

## Perfis de usuário e status

| Perfil | Descrição e permissões | Status |
|---|---|---|
| Aluno | Visualiza oportunidades, busca vagas, gerencia perfil e favoritos | Implementado |
| Professor | Divulga oportunidades de IC e gerencia candidaturas | Parcialmente implementado |
| Colaborador (Empresa) | Solicita registro da empresa e posta vagas de estágio | Não implementado (trabalho futuro) |

## Como executar o projeto localmente

### 1. Clone o repositório
```bash
git clone https://github.com/SEU-USUARIO/vagas-puc-rio.git
cd vagas-puc-rio
```

### 2. Crie e ative um ambiente virtual (recomendado)
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install django
```

### 4. Realize as migrações do banco de dados
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Inicie o servidor de desenvolvimento
```bash
python manage.py runserver
```

Acesse a aplicação em `http://127.0.0.1:8000/`.

Para criar um usuário administrador e acessar o painel do Django (`/admin`):
```bash
python manage.py createsuperuser
```
