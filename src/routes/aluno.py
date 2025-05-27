from flask import Blueprint, render_template, request
from src.models.database import db, Aluno, Turma, Disciplina, Nota, Atividade, TrabalhoExemplar, Colegio, Periodo
from sqlalchemy import func

# Cria o blueprint
aluno_bp = Blueprint('aluno', __name__)

@aluno_bp.route('/ranking')
def ranking():
    # Obter filtros da URL
    colegio_id = request.args.get('colegio', type=int)
    turma_id = request.args.get('turma', type=int)
    disciplina_id = request.args.get('disciplina', type=int)
    periodo_id = request.args.get('periodo', type=int)
    
    # Consulta base para alunos
    query = db.session.query(
        Aluno,
        func.sum(Nota.valor * Atividade.peso).label('xp'),
        func.avg(Nota.valor).label('media')
    ).join(Nota, Aluno.id == Nota.aluno_id, isouter=True) \
     .join(Atividade, Nota.atividade_id == Atividade.id, isouter=True) \
     .join(Turma, Aluno.turma_id == Turma.id)
    
    # Aplicar filtros
    if colegio_id:
        query = query.filter(Turma.colegio_id == colegio_id)
    
    if turma_id:
        query = query.filter(Aluno.turma_id == turma_id)
    
    if disciplina_id:
        query = query.filter(Atividade.disciplina_id == disciplina_id)
    
    if periodo_id:
        query = query.filter(Atividade.periodo_id == periodo_id)
    
    # Agrupar e ordenar
    alunos_data = query.group_by(Aluno.id).order_by(func.sum(Nota.valor * Atividade.peso).desc()).all()
    
    # Processar resultados
    alunos = []
    for aluno, xp, media in alunos_data:
        aluno.xp = int(xp) if xp else 0
        aluno.media = float(media) if media else 0
        alunos.append(aluno)
    
    # Obter dados para filtros
    colegios = Colegio.query.all()
    turmas = Turma.query.all()
    disciplinas = Disciplina.query.all()
    periodos = Periodo.query.all()
    
    return render_template('aluno/ranking.html', 
                          alunos=alunos,
                          colegios=colegios,
                          turmas=turmas,
                          disciplinas=disciplinas,
                          periodos=periodos)

@aluno_bp.route('/aluno/perfil/<int:id>')
def perfil(id):
    aluno = Aluno.query.get_or_404(id)
    
    # Obter notas do aluno
    notas = Nota.query.filter_by(aluno_id=id).all()
    
    # Calcular estatísticas
    total_xp = 0
    media_geral = 0
    
    if notas:
        for nota in notas:
            atividade = Atividade.query.get(nota.atividade_id)
            total_xp += nota.valor * atividade.peso
        
        media_geral = total_xp / len(notas)
    
    # Determinar nível e categoria
    nivel = (int(total_xp) // 100) + 1
    
    categoria = 'D'
    if media_geral >= 9.0:
        categoria = 'S'
    elif media_geral >= 8.0:
        categoria = 'A'
    elif media_geral >= 7.0:
        categoria = 'B'
    elif media_geral >= 6.0:
        categoria = 'C'
    
    # Obter trabalhos exemplares do aluno
    trabalhos = TrabalhoExemplar.query.filter_by(aluno_id=id).all()
    
    return render_template('aluno/perfil.html', 
                          aluno=aluno,
                          notas=notas,
                          total_xp=total_xp,
                          media_geral=media_geral,
                          nivel=nivel,
                          categoria=categoria,
                          trabalhos=trabalhos)

@aluno_bp.route('/aluno/linha-tempo/<int:id>')
def linha_tempo(id):
    aluno = Aluno.query.get_or_404(id)
    
    # Obter atividades e notas do aluno
    notas = db.session.query(Nota, Atividade) \
        .join(Atividade, Nota.atividade_id == Atividade.id) \
        .filter(Nota.aluno_id == id) \
        .order_by(Atividade.data_entrega) \
        .all()
    
    return render_template('aluno/linha_tempo.html', 
                          aluno=aluno,
                          notas=notas)

@aluno_bp.route('/aluno/trabalhos/<int:id>')
def trabalhos(id):
    aluno = Aluno.query.get_or_404(id)
    
    # Obter trabalhos exemplares do aluno
    trabalhos = TrabalhoExemplar.query.filter_by(aluno_id=id).all()
    
    return render_template('aluno/trabalhos.html', 
                          aluno=aluno,
                          trabalhos=trabalhos)
