from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from src.main import db

class Professor(UserMixin, db.Model):
    __tablename__ = 'professores'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    
    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)
        
    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)

class Colegio(db.Model):
    __tablename__ = 'colegios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(200))
    
    turmas = db.relationship('Turma', backref='colegio', lazy=True)

class Turma(db.Model):
    __tablename__ = 'turmas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    colegio_id = db.Column(db.Integer, db.ForeignKey('colegios.id'), nullable=False)
    
    alunos = db.relationship('Aluno', backref='turma', lazy=True)
    atividades = db.relationship('Atividade', backref='turma', lazy=True)

class Disciplina(db.Model):
    __tablename__ = 'disciplinas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    icone = db.Column(db.String(50))
    cor = db.Column(db.String(20))
    
    atividades = db.relationship('Atividade', backref='disciplina', lazy=True)

class Periodo(db.Model):
    __tablename__ = 'periodos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    
    atividades = db.relationship('Atividade', backref='periodo', lazy=True)

class Aluno(db.Model):
    __tablename__ = 'alunos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    foto = db.Column(db.String(200))
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)
    nivel = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    categoria = db.Column(db.String(50), default='Bronze')
    
    notas = db.relationship('Nota', backref='aluno', lazy=True)
    trabalhos = db.relationship('Trabalho', backref='aluno', lazy=True)

class Atividade(db.Model):
    __tablename__ = 'atividades'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_entrega = db.Column(db.Date, nullable=False)
    peso = db.Column(db.Float, default=1.0)
    xp_base = db.Column(db.Integer, default=100)
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplinas.id'), nullable=False)
    periodo_id = db.Column(db.Integer, db.ForeignKey('periodos.id'), nullable=False)
    
    notas = db.relationship('Nota', backref='atividade', lazy=True)

class Nota(db.Model):
    __tablename__ = 'notas'
    
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    xp_ganho = db.Column(db.Integer, nullable=False)
    data_lancamento = db.Column(db.DateTime, default=datetime.utcnow)
    trabalho_exemplar = db.Column(db.Boolean, default=False)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    atividade_id = db.Column(db.Integer, db.ForeignKey('atividades.id'), nullable=False)

class Trabalho(db.Model):
    __tablename__ = 'trabalhos'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    imagem = db.Column(db.String(200))
    data = db.Column(db.DateTime, default=datetime.utcnow)
    nota = db.Column(db.Float, nullable=False)
    comentario = db.Column(db.Text)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplinas.id'), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)
    periodo_id = db.Column(db.Integer, db.ForeignKey('periodos.id'), nullable=False)
