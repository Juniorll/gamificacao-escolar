import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar o aplicativo Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chave-secreta-padrao')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///gamificacao.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar o banco de dados
db = SQLAlchemy(app)

# Configuração do login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Função para carregar o usuário pelo ID (necessário para o Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    from src.models.database import Professor
    return Professor.query.get(int(user_id))

# Importar e registrar blueprints
from src.routes.auth import auth_bp
from src.routes.professor import professor_bp
from src.routes.aluno import aluno_bp

app.register_blueprint(auth_bp)
app.register_blueprint(professor_bp)
app.register_blueprint(aluno_bp)

# Rota raiz
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('professor.dashboard'))
    else:
        return redirect(url_for('auth.login'))

# Inicializar o banco de dados com alguns dados de exemplo
@app.before_first_request
def create_tables_and_sample_data():
    db.create_all()
    
    # Verificar se já existem dados
    from src.models.database import Professor, Colegio, Turma, Disciplina, Periodo, Aluno
    
    if Professor.query.count() == 0:
        # Criar professor de exemplo
        from werkzeug.security import generate_password_hash
        professor = Professor(nome='Professor Exemplo', email='professor@exemplo.com', 
                             senha_hash=generate_password_hash('senha123'))
        db.session.add(professor)
        
        # Criar colégio de exemplo
        colegio = Colegio(nome='Colégio Técnico', endereco='Rua Exemplo, 123')
        db.session.add(colegio)
        
        # Criar turma de exemplo
        turma = Turma(nome='Turma A', ano=2025, colegio=colegio)
        db.session.add(turma)
        
        # Criar disciplinas de exemplo
        disciplinas = [
            Disciplina(nome='Programação', descricao='Desenvolvimento de sistemas', 
                      icone='fa-code', cor='#4e73df'),
            Disciplina(nome='Banco de Dados', descricao='Modelagem e SQL', 
                      icone='fa-database', cor='#1cc88a'),
            Disciplina(nome='Redes', descricao='Infraestrutura de redes', 
                      icone='fa-network-wired', cor='#36b9cc')
        ]
        for disciplina in disciplinas:
            db.session.add(disciplina)
        
        # Criar período de exemplo
        periodo = Periodo(nome='1º Bimestre', data_inicio='2025-01-01', data_fim='2025-03-31')
        db.session.add(periodo)
        
        # Criar alunos de exemplo
        alunos = [
            Aluno(nome='João Silva', email='joao@exemplo.com', turma=turma, 
                 nivel=3, xp=350, categoria='Ouro'),
            Aluno(nome='Maria Santos', email='maria@exemplo.com', turma=turma, 
                 nivel=4, xp=450, categoria='Platina'),
            Aluno(nome='Pedro Oliveira', email='pedro@exemplo.com', turma=turma, 
                 nivel=2, xp=220, categoria='Prata')
        ]
        for aluno in alunos:
            db.session.add(aluno)
        
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
