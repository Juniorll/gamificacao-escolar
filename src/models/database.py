from flask_login import UserMixin
from src.main import db

class Professor(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha_hash = db.Column(db.String(200), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=db.func.current_timestamp())
    ativo = db.Column(db.Boolean, default=True)
    
    def get_id(self):
        return str(self.id)

class Colegio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(200))
    logo = db.Column(db.String(200))
    data_cadastro = db.Column(db.DateTime, default=db.func.current_timestamp())

class ProfessorColegio(db.Model):
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), primary_key=True)
    colegio_id = db.Column(db.Integer, db.ForeignKey('colegio.id'), primary_key=True)

class Turma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    colegio_id = db.Column(db.Integer, db.ForeignKey('colegio.id'), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=db.func.current_timestamp())

class Periodo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    periodo_pai_id = db.Column(db.Integer, db.ForeignKey('periodo.id'))

class Disciplina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    icone = db.Column(db.String(200))
    cor = db.Column(db.String(7), default='#3498db')
    data_cadastro = db.Column(db.DateTime, default=db.func.current_timestamp())

class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    foto = db.Column(db.String(200))
    avatar = db.Column(db.String(200))
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=db.func.current_timestamp())

class Atividade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    tipo = db.Column(db.String(50), nullable=False)
    valor_max = db.Column(db.Float, nullable=False)
    peso = db.Column(db.Float, default=1.0)
    data_entrega = db.Column(db.Date, nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplina.id'), nullable=False)
    periodo_id = db.Column(db.Integer, db.ForeignKey('periodo.id'), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=db.func.current_timestamp())

class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    atividade_id = db.Column(db.Integer, db.ForeignKey('atividade.id'), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    realizada = db.Column(db.Boolean, default=True)
    data_lancamento = db.Column(db.DateTime, default=db.func.current_timestamp())

class TrabalhoExemplar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    atividade_id = db.Column(db.Integer, db.ForeignKey('atividade.id'), nullable=False)
    descricao = db.Column(db.Text)
    link = db.Column(db.String(255))
    arquivo = db.Column(db.String(255))
    data_destaque = db.Column(db.DateTime, default=db.func.current_timestamp())

class Configuracao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(100), nullable=False, unique=True)
    valor = db.Column(db.Text, nullable=False)
    descricao = db.Column(db.Text)
