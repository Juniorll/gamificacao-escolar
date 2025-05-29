# Arquivo: src/routes/aluno.py
from flask import Blueprint, render_template, request, redirect, url_for
from src.models.database import Aluno, Turma, Disciplina, Periodo, Atividade, Nota, Trabalho, Colegio
from sqlalchemy.sql import func
from sqlalchemy import desc

aluno_bp = Blueprint('aluno', __name__)

@aluno_bp.route('/ranking')
def ranking():
    # Obter parâmetros de filtro
    colegio_id = request.args.get('colegio_id', type=int)
    turma_id = request.args.get('turma_id', type=int)
    disciplina_id = request.args.get('disciplina_id', type=int)
    periodo_id = request.args.get('periodo_id', type=int)
    
    # Consulta base para alunos
    query = Aluno.query
    
    # Aplicar filtros se fornecidos
    if turma_id:
        query = query.filter(Aluno.turma_id == turma_id)
    if colegio_id:
        query = query.join(Turma).filter(Turma.colegio_id == colegio_id)
    
    # Obter alunos ordenados por XP (decrescente)
    alunos = query.order_by(desc(Aluno.xp)).all()
    
    # Preparar dados para o template
    alunos_data = []
    for i, aluno in enumerate(alunos, 1):
        # Calcular próximo nível
        nivel_atual = aluno.nivel
        nivel_atual_xp = nivel_atual * 100  # Simplificado para exemplo
        proximo_nivel_xp = (nivel_atual + 1) * 100  # Simplificado para exemplo
        
        alunos_data.append({
            'id': aluno.id,
            'nome': aluno.nome,
            'foto': aluno.foto,
            'categoria': aluno.categoria,
            'categoria_cor': '#1cc88a',  # Cor padrão
            'nivel': aluno.nivel,
            'xp': aluno.xp,
            'nivel_atual_xp': nivel_atual_xp,
            'proximo_nivel_xp': proximo_nivel_xp
        })
    
    # Obter listas para filtros
    colegios = Colegio.query.all()
    turmas = Turma.query.all()
    disciplinas = Disciplina.query.all()
    periodos = Periodo.query.all()
    
    return render_template('aluno/ranking.html', 
                          alunos=alunos_data,
                          colegios=colegios,
                          turmas=turmas,
                          disciplinas=disciplinas,
                          periodos=periodos)

@aluno_bp.route('/perfil/<int:id>')
def perfil(id):
    # Obter aluno pelo ID
    aluno = Aluno.query.get_or_404(id)
    
    # Dados simulados para o template
    aluno_data = {
        'id': aluno.id,
        'nome': aluno.nome,
        'foto': aluno.foto,
        'turma': {'nome': 'Turma Exemplo', 'colegio': {'nome': 'Colégio Exemplo'}},
        'categoria': 'Lendário',
        'categoria_cor': '#1cc88a',
        'nivel': 5,
        'xp': 550,
        'nivel_atual_xp': 500,
        'proximo_nivel_xp': 600,
        'ranking': 1,
        'atividades_concluidas': 15,
        'media_geral': 8.5,
        'trabalhos_exemplares': 3,
        'chance_aprovacao': 85
    }
    
    # Dados simulados para atividades
    atividades = [
        {
            'titulo': 'Atividade Exemplo 1',
            'descricao': 'Descrição da atividade exemplo 1',
            'data_entrega': func.now(),
            'disciplina_id': 1,
            'disciplina_nome': 'Programação',
            'disciplina_cor': '#4e73df',
            'status': 'concluido',
            'nota': 9.0
        },
        {
            'titulo': 'Atividade Exemplo 2',
            'descricao': 'Descrição da atividade exemplo 2',
            'data_entrega': func.now(),
            'disciplina_id': 2,
            'disciplina_nome': 'Banco de Dados',
            'disciplina_cor': '#1cc88a',
            'status': 'pendente',
            'nota': None
        }
    ]
    
    # Dados simulados para trabalhos exemplares
    trabalhos_exemplares = [
        {
            'id': 1,
            'titulo': 'Trabalho Exemplo 1',
            'descricao': 'Descrição do trabalho exemplo 1',
            'disciplina_nome': 'Programação',
            'imagem': None,
            'data': func.now(),
            'nota': 10.0
        }
    ]
    
    # Dados simulados para desempenho por disciplina
    desempenho_disciplinas = [
        {
            'nome': 'Programação',
            'cor': '#4e73df',
            'icone': 'fas fa-code',
            'media': 9.0
        },
        {
            'nome': 'Banco de Dados',
            'cor': '#1cc88a',
            'icone': 'fas fa-database',
            'media': 8.0
        }
    ]
    
    # Dados simulados para próximas atividades
    proximas_atividades = [
        {
            'titulo': 'Próxima Atividade 1',
            'disciplina_nome': 'Programação',
            'data_entrega': func.now()
        }
    ]
    
    # Obter disciplinas para filtro
    disciplinas = Disciplina.query.all()
    
    return render_template('aluno/perfil.html',
                          aluno=aluno_data,
                          atividades=atividades,
                          trabalhos_exemplares=trabalhos_exemplares,
                          desempenho_disciplinas=desempenho_disciplinas,
                          proximas_atividades=proximas_atividades,
                          disciplinas=disciplinas)

@aluno_bp.route('/trabalhos')
def trabalhos():
    # Obter parâmetros de filtro
    disciplina_id = request.args.get('disciplina_id', type=int)
    turma_id = request.args.get('turma_id', type=int)
    periodo_id = request.args.get('periodo_id', type=int)
    ordenar = request.args.get('ordenar', 'data')
    
    # Dados simulados para trabalhos exemplares
    trabalhos = [
        {
            'id': 1,
            'titulo': 'Trabalho Exemplo 1',
            'descricao': 'Descrição detalhada do trabalho exemplo 1. Este trabalho demonstra excelente domínio dos conceitos de programação orientada a objetos.',
            'disciplina_id': 1,
            'disciplina_nome': 'Programação',
            'disciplina_cor': '#4e73df',
            'turma_id': 1,
            'turma_nome': 'Turma Exemplo',
            'aluno_id': 1,
            'aluno_nome': 'Aluno Exemplo',
            'aluno_foto': None,
            'imagem': None,
            'data': func.now(),
            'nota': 10.0,
            'comentario': 'Excelente trabalho! Demonstra domínio completo do conteúdo.'
        },
        {
            'id': 2,
            'titulo': 'Trabalho Exemplo 2',
            'descricao': 'Descrição detalhada do trabalho exemplo 2. Este projeto de banco de dados apresenta uma modelagem eficiente e normalizada.',
            'disciplina_id': 2,
            'disciplina_nome': 'Banco de Dados',
            'disciplina_cor': '#1cc88a',
            'turma_id': 1,
            'turma_nome': 'Turma Exemplo',
            'aluno_id': 2,
            'aluno_nome': 'Outro Aluno',
            'aluno_foto': None,
            'imagem': None,
            'data': func.now(),
            'nota': 9.5,
            'comentario': 'Muito bom trabalho! A modelagem está bem estruturada.'
        }
    ]
    
    # Filtrar trabalhos se necessário
    if disciplina_id:
        trabalhos = [t for t in trabalhos if t['disciplina_id'] == disciplina_id]
    if turma_id:
        trabalhos = [t for t in trabalhos if t['turma_id'] == turma_id]
    
    # Ordenar trabalhos
    if ordenar == 'nota':
        trabalhos = sorted(trabalhos, key=lambda t: t['nota'], reverse=True)
    elif ordenar == 'aluno':
        trabalhos = sorted(trabalhos, key=lambda t: t['aluno_nome'])
    else:  # data (padrão)
        trabalhos = sorted(trabalhos, key=lambda t: t['data'], reverse=True)
    
    # Obter listas para filtros
    disciplinas = Disciplina.query.all()
    turmas = Turma.query.all()
    periodos = Periodo.query.all()
    
    return render_template('aluno/trabalhos.html',
                          trabalhos=trabalhos,
                          disciplinas=disciplinas,
                          turmas=turmas,
                          periodos=periodos)
