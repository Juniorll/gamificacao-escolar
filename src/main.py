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
        
        # Adiciona rota raiz para redirecionar para a página de login
        @app.route('/')
        def index():
            return redirect(url_for('auth.login'))
        
        # Rota alternativa para página inicial personalizada
        @app.route('/home')
        def home():
            return render_template('index.html')
        
        # Cria tabelas do banco de dados se não existirem
        db.create_all()
    
    return app

# Cria a instância do aplicativo para uso com Gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
