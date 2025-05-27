from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.models.database import db, Professor, Colegio, Turma, Disciplina, Periodo, Aluno, Atividade, Nota

# Cria o blueprint
professor_bp = Blueprint('professor', __name__)

@professor_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('professor/dashboard.html')

# Adicione aqui as outras rotas do professor
