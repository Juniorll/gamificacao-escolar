import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa extensões sem vincular a um aplicativo específico
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """
    Função de fábrica de aplicativo que cria e configura a instância do Flask.
    """
    app = Flask(__name__)
    
    # Configuração do aplicativo
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chave-secreta-padrao')
    
    # Configuração do banco de dados
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Supabase ou Render PostgreSQL fornece URL no formato: postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/postgres
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Configuração local para desenvolvimento
        app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USERNAME', 'postgres')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'postgres')}"
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializa extensões com o aplicativo
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Importa e registra blueprints
    with app.app_context():
        # Importações dentro do contexto para evitar erros de contexto
        from src.routes.auth import auth_bp
        from src.routes.professor import professor_bp
        from src.routes.aluno import aluno_bp
        from src.routes.admin import admin_bp
        
        # Registra blueprints
        app.register_blueprint(auth_bp)
        app.register_blueprint(professor_bp)
        app.register_blueprint(aluno_bp)
        app.register_blueprint(admin_bp)
        
        # Configura o carregador de usuário
        @login_manager.user_loader
        def load_user(user_id):
            from src.models.database import Professor
            return Professor.query.get(int(user_id))
        
        # Adiciona rota raiz para redirecionar para a página inicial
        @app.route('/')
        def index():
            return redirect(url_for('auth.login'))
        
        # Rota para página inicial personalizada
        @app.route('/home')
        def home():
            return render_template('index.html')
        
        # Cria tabelas do banco de dados se não existirem
        db.create_all()
        
        # Inicializa dados de exemplo se o banco estiver vazio
        inicializar_dados_exemplo(db)
    
    return app

def inicializar_dados_exemplo(db):
    """
    Inicializa dados de exemplo no banco de dados se estiver vazio.
    """
    from src.models.database import Professor, Colegio, Turma, Disciplina, Periodo, Aluno
    from werkzeug.security import generate_password_hash
    
    # Verificar se já existem dados
    if Professor.query.count() > 0:
        return
    
    # Criar professor de exemplo
    professor = Professor(
        nome="Professor Exemplo",
        email="professor@exemplo.com",
        senha_hash=generate_password_hash("senha123")
    )
    db.session.add(professor)
    db.session.commit()
    
    # Criar colégio de exemplo
    colegio = Colegio(
        nome="Colégio Técnico Exemplo",
        endereco="Rua das Escolas, 123"
    )
    db.session.add(colegio)
    db.session.commit()
    
    # Criar turma de exemplo
    turma = Turma(
        nome="Turma 3º Ano - Desenvolvimento de Sistemas",
        ano=2025,
        professor_id=professor.id,
        colegio_id=colegio.id
    )
    db.session.add(turma)
    db.session.commit()
    
    # Criar disciplinas de exemplo
    disciplinas = [
        Disciplina(
            nome="Programação Web",
            descricao="Desenvolvimento de aplicações web com HTML, CSS e JavaScript",
            professor_id=professor.id,
            icone="fa-globe",
            cor="#3498db"
        ),
        Disciplina(
            nome="Banco de Dados",
            descricao="Modelagem e implementação de bancos de dados relacionais",
            professor_id=professor.id,
            icone="fa-database",
            cor="#2ecc71"
        ),
        Disciplina(
            nome="Desenvolvimento Mobile",
            descricao="Criação de aplicativos para dispositivos móveis",
            professor_id=professor.id,
            icone="fa-mobile-alt",
            cor="#e74c3c"
        )
    ]
    
    for disciplina in disciplinas:
        db.session.add(disciplina)
    db.session.commit()
    
    # Criar períodos de exemplo
    periodo_ano = Periodo(
        nome="Ano Letivo 2025",
        data_inicio="2025-02-01",
        data_fim="2025-12-15",
        tipo="Ano"
    )
    db.session.add(periodo_ano)
    db.session.commit()
    
    periodos = [
        Periodo(
            nome="1º Bimestre",
            data_inicio="2025-02-01",
            data_fim="2025-04-15",
            tipo="Bimestre",
            periodo_pai_id=periodo_ano.id
        ),
        Periodo(
            nome="2º Bimestre",
            data_inicio="2025-04-16",
            data_fim="2025-06-30",
            tipo="Bimestre",
            periodo_pai_id=periodo_ano.id
        ),
        Periodo(
            nome="3º Bimestre",
            data_inicio="2025-08-01",
            data_fim="2025-10-15",
            tipo="Bimestre",
            periodo_pai_id=periodo_ano.id
        ),
        Periodo(
            nome="4º Bimestre",
            data_inicio="2025-10-16",
            data_fim="2025-12-15",
            tipo="Bimestre",
            periodo_pai_id=periodo_ano.id
        )
    ]
    
    for periodo in periodos:
        db.session.add(periodo)
    db.session.commit()
    
    # Criar alunos de exemplo
    alunos = [
        Aluno(
            nome="Ana Silva",
            email="ana.silva@aluno.exemplo.com",
            turma_id=turma.id
        ),
        Aluno(
            nome="Bruno Santos",
            email="bruno.santos@aluno.exemplo.com",
            turma_id=turma.id
        ),
        Aluno(
            nome="Carla Oliveira",
            email="carla.oliveira@aluno.exemplo.com",
            turma_id=turma.id
        ),
        Aluno(
            nome="Daniel Pereira",
            email="daniel.pereira@aluno.exemplo.com",
            turma_id=turma.id
        ),
        Aluno(
            nome="Eduarda Costa",
            email="eduarda.costa@aluno.exemplo.com",
            turma_id=turma.id
        )
    ]
    
    for aluno in alunos:
        db.session.add(aluno)
    db.session.commit()

# Cria a instância do aplicativo para uso com Gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
