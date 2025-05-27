"""
Módulo de configuração do banco de dados e definição dos modelos.
Este arquivo contém a configuração do SQLAlchemy e os modelos de dados
para o sistema de gamificação escolar.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

# Inicialização do SQLAlchemy
db = SQLAlchemy()

# Tabela de associação entre professores e colégios
professor_colegio = db.Table('professor_colegio',
    db.Column('professor_id', db.Integer, db.ForeignKey('professor.id'), primary_key=True),
    db.Column('colegio_id', db.Integer, db.ForeignKey('colegio.id'), primary_key=True)
)

class Professor(UserMixin, db.Model):
    """Modelo para professores que podem fazer login no sistema."""
    __tablename__ = 'professor'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    colegios = db.relationship('Colegio', secondary=professor_colegio, 
                              backref=db.backref('professores', lazy='dynamic'))
    turmas = db.relationship('Turma', backref='professor', lazy=True)
    disciplinas = db.relationship('Disciplina', backref='professor', lazy=True)
    atividades = db.relationship('Atividade', backref='professor', lazy=True)
    
    def __repr__(self):
        return f'<Professor {self.nome}>'

class Colegio(db.Model):
    """Modelo para colégios cadastrados no sistema."""
    __tablename__ = 'colegio'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(200))
    logo = db.Column(db.String(200))  # Caminho para o arquivo de logo
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    turmas = db.relationship('Turma', backref='colegio', lazy=True)
    
    def __repr__(self):
        return f'<Colegio {self.nome}>'

class Turma(db.Model):
    """Modelo para turmas cadastradas no sistema."""
    __tablename__ = 'turma'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    colegio_id = db.Column(db.Integer, db.ForeignKey('colegio.id'), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    alunos = db.relationship('Aluno', backref='turma', lazy=True)
    
    def __repr__(self):
        return f'<Turma {self.nome} - {self.ano}>'

class Periodo(db.Model):
    """Modelo para períodos letivos (ano, semestre, trimestre, etc.)."""
    __tablename__ = 'periodo'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # ano, semestre, trimestre, etc.
    periodo_pai_id = db.Column(db.Integer, db.ForeignKey('periodo.id'), nullable=True)
    
    # Relacionamentos
    subperiodos = db.relationship('Periodo', backref=db.backref('periodo_pai', remote_side=[id]))
    atividades = db.relationship('Atividade', backref='periodo', lazy=True)
    
    def __repr__(self):
        return f'<Periodo {self.nome} ({self.tipo})>'

class Disciplina(db.Model):
    """Modelo para disciplinas cadastradas no sistema."""
    __tablename__ = 'disciplina'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    icone = db.Column(db.String(200))  # Caminho para o arquivo de ícone
    cor = db.Column(db.String(7), default='#3498db')  # Cor em hexadecimal
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    atividades = db.relationship('Atividade', backref='disciplina', lazy=True)
    
    def __repr__(self):
        return f'<Disciplina {self.nome}>'

class Aluno(db.Model):
    """Modelo para alunos cadastrados no sistema."""
    __tablename__ = 'aluno'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    foto = db.Column(db.String(200))  # Caminho para o arquivo de foto
    avatar = db.Column(db.String(200))  # Caminho para o avatar (alternativa à foto)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    notas = db.relationship('Nota', backref='aluno', lazy=True)
    
    # Propriedades calculadas
    @property
    def xp_total(self):
        """Calcula o total de XP (pontos) do aluno."""
        return sum(nota.valor for nota in self.notas if nota.atividade.tipo != 'trabalho_exemplar')
    
    @property
    def nivel(self):
        """Calcula o nível do aluno com base no XP total."""
        xp = self.xp_total
        # Definição dos níveis (pode ser ajustada)
        if xp >= 1000:
            return {"nivel": 5, "titulo": "Desenvolvedor Sênior"}
        elif xp >= 750:
            return {"nivel": 4, "titulo": "Desenvolvedor Pleno"}
        elif xp >= 500:
            return {"nivel": 3, "titulo": "Desenvolvedor Júnior"}
        elif xp >= 250:
            return {"nivel": 2, "titulo": "Programador Iniciante"}
        else:
            return {"nivel": 1, "titulo": "Aprendiz de Código"}
    
    @property
    def categoria(self):
        """Define a categoria do aluno com base na média de notas."""
        notas = [nota.valor for nota in self.notas]
        if not notas:
            return {"nome": "Novato", "cor": "#CCCCCC", "icone": "novato.gif"}
        
        media = sum(notas) / len(notas)
        
        if media >= 90:
            return {"nome": "Hacker Lendário", "cor": "#FFD700", "icone": "hacker_lendario.gif"}
        elif media >= 85:
            return {"nome": "Mestre do Código", "cor": "#C0C0C0", "icone": "mestre_codigo.gif"}
        elif media >= 80:
            return {"nome": "Desenvolvedor Elite", "cor": "#CD7F32", "icone": "dev_elite.gif"}
        elif media >= 75:
            return {"nome": "Programador Avançado", "cor": "#9370DB", "icone": "prog_avancado.gif"}
        elif media >= 70:
            return {"nome": "Codificador Experiente", "cor": "#3498db", "icone": "codificador.gif"}
        elif media >= 60:
            return {"nome": "Aprendiz de Algoritmos", "cor": "#2ecc71", "icone": "aprendiz.gif"}
        else:
            return {"nome": "Iniciante em Bits", "cor": "#e74c3c", "icone": "iniciante.gif"}
    
    def __repr__(self):
        return f'<Aluno {self.nome}>'

class Atividade(db.Model):
    """Modelo para atividades cadastradas no sistema."""
    __tablename__ = 'atividade'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    tipo = db.Column(db.String(50), nullable=False)  # prova, trabalho, exercício, etc.
    valor_max = db.Column(db.Float, nullable=False)  # Valor máximo da atividade (pontos)
    peso = db.Column(db.Float, default=1.0)  # Peso da atividade na média
    data_entrega = db.Column(db.Date, nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplina.id'), nullable=False)
    periodo_id = db.Column(db.Integer, db.ForeignKey('periodo.id'), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    notas = db.relationship('Nota', backref='atividade', lazy=True)
    trabalhos_exemplares = db.relationship('TrabalhoExemplar', backref='atividade', lazy=True)
    
    def __repr__(self):
        return f'<Atividade {self.titulo}>'

class Nota(db.Model):
    """Modelo para notas dos alunos nas atividades."""
    __tablename__ = 'nota'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    atividade_id = db.Column(db.Integer, db.ForeignKey('atividade.id'), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    realizada = db.Column(db.Boolean, default=True)
    data_lancamento = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Nota {self.aluno_id} - {self.atividade_id}: {self.valor}>'

class TrabalhoExemplar(db.Model):
    """Modelo para trabalhos exemplares destacados pelos professores."""
    __tablename__ = 'trabalho_exemplar'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    atividade_id = db.Column(db.Integer, db.ForeignKey('atividade.id'), nullable=False)
    descricao = db.Column(db.Text)
    link = db.Column(db.String(255))  # Link para o trabalho, se disponível
    arquivo = db.Column(db.String(255))  # Caminho para o arquivo, se disponível
    data_destaque = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    aluno = db.relationship('Aluno', backref='trabalhos_exemplares')
    
    def __repr__(self):
        return f'<TrabalhoExemplar {self.aluno_id} - {self.atividade_id}>'

class Configuracao(db.Model):
    """Modelo para configurações personalizadas do sistema."""
    __tablename__ = 'configuracao'
    
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Text, nullable=False)
    descricao = db.Column(db.Text)
    
    def get_valor_json(self):
        """Retorna o valor como objeto JSON, se aplicável."""
        try:
            return json.loads(self.valor)
        except:
            return self.valor
    
    def __repr__(self):
        return f'<Configuracao {self.chave}>'
