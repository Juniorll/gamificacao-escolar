from flask import Blueprint, render_template, request
from src.models.database import db, Aluno, Turma, Disciplina, Nota, Atividade, TrabalhoExemplar

# Cria o blueprint
aluno_bp = Blueprint('aluno', __name__)

@aluno_bp.route('/ranking')
def ranking():
    return render_template('aluno/ranking.html')

# Adicione aqui as outras rotas do aluno
