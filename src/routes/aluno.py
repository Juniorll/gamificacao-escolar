"""
Módulo de rotas para visualização de dados pelos alunos.
Este arquivo contém as rotas para visualização de rankings, linha do tempo e outras informações gamificadas.
"""

from flask import Blueprint, request, jsonify
from src.models.database import db, Aluno, Turma, Colegio, Disciplina, Periodo, Atividade, Nota, TrabalhoExemplar
from sqlalchemy import func, desc
import datetime

# Criação do blueprint do aluno (visualização pública, sem autenticação)
aluno_bp = Blueprint("aluno", __name__)

@aluno_bp.route("/ranking/geral", methods=["GET"])
def ranking_geral():
    """
    Retorna o ranking geral de todos os alunos com base nas notas.
    """
    # Subconsulta para calcular a média de notas por aluno
    subquery = db.session.query(
        Nota.aluno_id,
        func.avg(Nota.valor).label('media')
    ).group_by(Nota.aluno_id).subquery()
    
    # Consulta principal juntando com a tabela de alunos
    alunos_ranking = db.session.query(
        Aluno.id,
        Aluno.nome,
        Aluno.foto,
        Aluno.avatar,
        Turma.nome.label('turma_nome'),
        Colegio.nome.label('colegio_nome'),
        subquery.c.media
    ).join(
        subquery, Aluno.id == subquery.c.aluno_id
    ).join(
        Turma, Aluno.turma_id == Turma.id
    ).join(
        Colegio, Turma.colegio_id == Colegio.id
    ).order_by(
        desc(subquery.c.media)
    ).all()
    
    # Formatar resultado
    resultado = []
    for i, aluno in enumerate(alunos_ranking):
        # Calcular categoria com base na média
        categoria = calcular_categoria(aluno.media)
        
        # Calcular nível com base no XP total
        nivel = calcular_nivel(aluno.id)
        
        resultado.append({
            "posicao": i + 1,
            "id": aluno.id,
            "nome": aluno.nome,
            "foto": aluno.foto,
            "avatar": aluno.avatar,
            "turma": aluno.turma_nome,
            "colegio": aluno.colegio_nome,
            "media": round(aluno.media, 2),
            "categoria": categoria,
            "nivel": nivel
        })
    
    return jsonify(resultado), 200

@aluno_bp.route("/ranking/colegio/<int:colegio_id>", methods=["GET"])
def ranking_por_colegio(colegio_id):
    """
    Retorna o ranking de alunos de um colégio específico.
    """
    # Verificar se o colégio existe
    colegio = Colegio.query.get(colegio_id)
    if not colegio:
        return jsonify({"mensagem": "Colégio não encontrado"}), 404
    
    # Subconsulta para calcular a média de notas por aluno
    subquery = db.session.query(
        Nota.aluno_id,
        func.avg(Nota.valor).label('media')
    ).group_by(Nota.aluno_id).subquery()
    
    # Consulta principal filtrando por colégio
    alunos_ranking = db.session.query(
        Aluno.id,
        Aluno.nome,
        Aluno.foto,
        Aluno.avatar,
        Turma.nome.label('turma_nome'),
        subquery.c.media
    ).join(
        subquery, Aluno.id == subquery.c.aluno_id
    ).join(
        Turma, Aluno.turma_id == Turma.id
    ).filter(
        Turma.colegio_id == colegio_id
    ).order_by(
        desc(subquery.c.media)
    ).all()
    
    # Formatar resultado
    resultado = []
    for i, aluno in enumerate(alunos_ranking):
        categoria = calcular_categoria(aluno.media)
        nivel = calcular_nivel(aluno.id)
        
        resultado.append({
            "posicao": i + 1,
            "id": aluno.id,
            "nome": aluno.nome,
            "foto": aluno.foto,
            "avatar": aluno.avatar,
            "turma": aluno.turma_nome,
            "media": round(aluno.media, 2),
            "categoria": categoria,
            "nivel": nivel
        })
    
    return jsonify(resultado), 200

@aluno_bp.route("/ranking/turma/<int:turma_id>", methods=["GET"])
def ranking_por_turma(turma_id):
    """
    Retorna o ranking de alunos de uma turma específica.
    """
    # Verificar se a turma existe
    turma = Turma.query.get(turma_id)
    if not turma:
        return jsonify({"mensagem": "Turma não encontrada"}), 404
    
    # Subconsulta para calcular a média de notas por aluno
    subquery = db.session.query(
        Nota.aluno_id,
        func.avg(Nota.valor).label('media')
    ).group_by(Nota.aluno_id).subquery()
    
    # Consulta principal filtrando por turma
    alunos_ranking = db.session.query(
        Aluno.id,
        Aluno.nome,
        Aluno.foto,
        Aluno.avatar,
        subquery.c.media
    ).join(
        subquery, Aluno.id == subquery.c.aluno_id
    ).filter(
        Aluno.turma_id == turma_id
    ).order_by(
        desc(subquery.c.media)
    ).all()
    
    # Formatar resultado
    resultado = []
    for i, aluno in enumerate(alunos_ranking):
        categoria = calcular_categoria(aluno.media)
        nivel = calcular_nivel(aluno.id)
        
        resultado.append({
            "posicao": i + 1,
            "id": aluno.id,
            "nome": aluno.nome,
            "foto": aluno.foto,
            "avatar": aluno.avatar,
            "media": round(aluno.media, 2),
            "categoria": categoria,
            "nivel": nivel
        })
    
    return jsonify(resultado), 200

@aluno_bp.route("/ranking/disciplina/<int:disciplina_id>", methods=["GET"])
def ranking_por_disciplina(disciplina_id):
    """
    Retorna o ranking de alunos em uma disciplina específica.
    """
    # Verificar se a disciplina existe
    disciplina = Disciplina.query.get(disciplina_id)
    if not disciplina:
        return jsonify({"mensagem": "Disciplina não encontrada"}), 404
    
    # Subconsulta para calcular a média de notas por aluno na disciplina específica
    subquery = db.session.query(
        Nota.aluno_id,
        func.avg(Nota.valor).label('media')
    ).join(
        Atividade, Nota.atividade_id == Atividade.id
    ).filter(
        Atividade.disciplina_id == disciplina_id
    ).group_by(Nota.aluno_id).subquery()
    
    # Consulta principal
    alunos_ranking = db.session.query(
        Aluno.id,
        Aluno.nome,
        Aluno.foto,
        Aluno.avatar,
        Turma.nome.label('turma_nome'),
        Colegio.nome.label('colegio_nome'),
        subquery.c.media
    ).join(
        subquery, Aluno.id == subquery.c.aluno_id
    ).join(
        Turma, Aluno.turma_id == Turma.id
    ).join(
        Colegio, Turma.colegio_id == Colegio.id
    ).order_by(
        desc(subquery.c.media)
    ).all()
    
    # Formatar resultado
    resultado = []
    for i, aluno in enumerate(alunos_ranking):
        categoria = calcular_categoria(aluno.media)
        nivel = calcular_nivel(aluno.id)
        
        resultado.append({
            "posicao": i + 1,
            "id": aluno.id,
            "nome": aluno.nome,
            "foto": aluno.foto,
            "avatar": aluno.avatar,
            "turma": aluno.turma_nome,
            "colegio": aluno.colegio_nome,
            "media": round(aluno.media, 2),
            "categoria": categoria,
            "nivel": nivel
        })
    
    return jsonify(resultado), 200

@aluno_bp.route("/ranking/periodo/<int:periodo_id>", methods=["GET"])
def ranking_por_periodo(periodo_id):
    """
    Retorna o ranking de alunos em um período específico.
    """
    # Verificar se o período existe
    periodo = Periodo.query.get(periodo_id)
    if not periodo:
        return jsonify({"mensagem": "Período não encontrado"}), 404
    
    # Subconsulta para calcular a média de notas por aluno no período específico
    subquery = db.session.query(
        Nota.aluno_id,
        func.avg(Nota.valor).label('media')
    ).join(
        Atividade, Nota.atividade_id == Atividade.id
    ).filter(
        Atividade.periodo_id == periodo_id
    ).group_by(Nota.aluno_id).subquery()
    
    # Consulta principal
    alunos_ranking = db.session.query(
        Aluno.id,
        Aluno.nome,
        Aluno.foto,
        Aluno.avatar,
        Turma.nome.label('turma_nome'),
        Colegio.nome.label('colegio_nome'),
        subquery.c.media
    ).join(
        subquery, Aluno.id == subquery.c.aluno_id
    ).join(
        Turma, Aluno.turma_id == Turma.id
    ).join(
        Colegio, Turma.colegio_id == Colegio.id
    ).order_by(
        desc(subquery.c.media)
    ).all()
    
    # Formatar resultado
    resultado = []
    for i, aluno in enumerate(alunos_ranking):
        categoria = calcular_categoria(aluno.media)
        nivel = calcular_nivel(aluno.id)
        
        resultado.append({
            "posicao": i + 1,
            "id": aluno.id,
            "nome": aluno.nome,
            "foto": aluno.foto,
            "avatar": aluno.avatar,
            "turma": aluno.turma_nome,
            "colegio": aluno.colegio_nome,
            "media": round(aluno.media, 2),
            "categoria": categoria,
            "nivel": nivel
        })
    
    return jsonify(resultado), 200

@aluno_bp.route("/aluno/<int:aluno_id>/linha_tempo", methods=["GET"])
def linha_tempo_aluno(aluno_id):
    """
    Retorna a linha do tempo de atividades de um aluno específico.
    """
    # Verificar se o aluno existe
    aluno = Aluno.query.get(aluno_id)
    if not aluno:
        return jsonify({"mensagem": "Aluno não encontrado"}), 404
    
    # Consulta para obter todas as atividades e notas do aluno
    atividades_notas = db.session.query(
        Atividade.id,
        Atividade.titulo,
        Atividade.descricao,
        Atividade.tipo,
        Atividade.valor_max,
        Atividade.peso,
        Atividade.data_entrega,
        Disciplina.nome.label('disciplina_nome'),
        Disciplina.cor.label('disciplina_cor'),
        Periodo.nome.label('periodo_nome'),
        Nota.valor,
        Nota.realizada,
        Nota.data_lancamento,
        TrabalhoExemplar.id.label('trabalho_exemplar_id')
    ).join(
        Disciplina, Atividade.disciplina_id == Disciplina.id
    ).join(
        Periodo, Atividade.periodo_id == Periodo.id
    ).outerjoin(
        Nota, (Nota.atividade_id == Atividade.id) & (Nota.aluno_id == aluno_id)
    ).outerjoin(
        TrabalhoExemplar, (TrabalhoExemplar.atividade_id == Atividade.id) & (TrabalhoExemplar.aluno_id == aluno_id)
    ).order_by(
        Atividade.data_entrega
    ).all()
    
    # Calcular média momentânea
    notas = [a.valor for a in atividades_notas if a.valor is not None]
    media_momentanea = sum(notas) / len(notas) if notas else 0
    
    # Calcular XP total
    xp_total = sum(a.valor for a in atividades_notas if a.valor is not None)
    xp_maximo = sum(a.valor_max for a in atividades_notas)
    
    # Formatar resultado
    linha_tempo = []
    for atividade in atividades_notas:
        status = "pendente"
        if atividade.realizada is not None:
            status = "realizada" if atividade.realizada else "nao_realizada"
        
        # Verificar se é um trabalho exemplar
        e_trabalho_exemplar = atividade.trabalho_exemplar_id is not None
        
        linha_tempo.append({
            "id": atividade.id,
            "titulo": atividade.titulo,
            "descricao": atividade.descricao,
            "tipo": atividade.tipo,
            "valor_max": atividade.valor_max,
            "peso": atividade.peso,
            "data_entrega": atividade.data_entrega.isoformat(),
            "disciplina": atividade.disciplina_nome,
            "disciplina_cor": atividade.disciplina_cor,
            "periodo": atividade.periodo_nome,
            "nota": atividade.valor,
            "status": status,
            "trabalho_exemplar": e_trabalho_exemplar
        })
    
    # Calcular chance de aprovação
    chance_aprovacao = calcular_chance_aprovacao(media_momentanea, atividades_notas)
    
    # Obter categoria e nível
    categoria = calcular_categoria(media_momentanea)
    nivel = calcular_nivel(aluno_id)
    
    resultado = {
        "aluno": {
            "id": aluno.id,
            "nome": aluno.nome,
            "foto": aluno.foto,
            "avatar": aluno.avatar,
            "turma": aluno.turma.nome,
            "colegio": aluno.turma.colegio.nome
        },
        "media_momentanea": round(media_momentanea, 2),
        "xp": {
            "total": xp_total,
            "maximo": xp_maximo,
            "percentual": round((xp_total / xp_maximo * 100) if xp_maximo > 0 else 0, 2)
        },
        "categoria": categoria,
        "nivel": nivel,
        "chance_aprovacao": chance_aprovacao,
        "linha_tempo": linha_tempo
    }
    
    return jsonify(resultado), 200

@aluno_bp.route("/trabalhos_exemplares", methods=["GET"])
def listar_trabalhos_exemplares():
    """
    Retorna a lista de trabalhos exemplares.
    """
    trabalhos = db.session.query(
        TrabalhoExemplar.id,
        TrabalhoExemplar.descricao,
        TrabalhoExemplar.link,
        TrabalhoExemplar.arquivo,
        TrabalhoExemplar.data_destaque,
        Aluno.id.label('aluno_id'),
        Aluno.nome.label('aluno_nome'),
        Aluno.foto.label('aluno_foto'),
        Aluno.avatar.label('aluno_avatar'),
        Atividade.titulo.label('atividade_titulo'),
        Disciplina.nome.label('disciplina_nome'),
        Disciplina.cor.label('disciplina_cor')
    ).join(
        Aluno, TrabalhoExemplar.aluno_id == Aluno.id
    ).join(
        Atividade, TrabalhoExemplar.atividade_id == Atividade.id
    ).join(
        Disciplina, Atividade.disciplina_id == Disciplina.id
    ).order_by(
        TrabalhoExemplar.data_destaque.desc()
    ).all()
    
    resultado = []
    for trabalho in trabalhos:
        resultado.append({
            "id": trabalho.id,
            "descricao": trabalho.descricao,
            "link": trabalho.link,
            "arquivo": trabalho.arquivo,
            "data_destaque": trabalho.data_destaque.isoformat(),
            "aluno": {
                "id": trabalho.aluno_id,
                "nome": trabalho.aluno_nome,
                "foto": trabalho.aluno_foto,
                "avatar": trabalho.aluno_avatar
            },
            "atividade": trabalho.atividade_titulo,
            "disciplina": trabalho.disciplina_nome,
            "disciplina_cor": trabalho.disciplina_cor
        })
    
    return jsonify(resultado), 200

@aluno_bp.route("/filtros", methods=["GET"])
def obter_filtros():
    """
    Retorna as opções de filtros disponíveis (colégios, turmas, disciplinas, períodos).
    """
    colegios = Colegio.query.all()
    turmas = Turma.query.all()
    disciplinas = Disciplina.query.all()
    periodos = Periodo.query.all()
    
    resultado = {
        "colegios": [{"id": c.id, "nome": c.nome} for c in colegios],
        "turmas": [{"id": t.id, "nome": t.nome, "colegio_id": t.colegio_id} for t in turmas],
        "disciplinas": [{"id": d.id, "nome": d.nome} for d in disciplinas],
        "periodos": [{"id": p.id, "nome": p.nome, "tipo": p.tipo} for p in periodos]
    }
    
    return jsonify(resultado), 200

@aluno_bp.route("/aluno/<int:aluno_id>/chance_aprovacao", methods=["GET"])
def chance_aprovacao(aluno_id):
    """
    Calcula e retorna a chance de aprovação de um aluno específico.
    """
    # Verificar se o aluno existe
    aluno = Aluno.query.get(aluno_id)
    if not aluno:
        return jsonify({"mensagem": "Aluno não encontrado"}), 404
    
    # Consulta para obter todas as atividades e notas do aluno
    atividades_notas = db.session.query(
        Atividade.id,
        Atividade.titulo,
        Atividade.valor_max,
        Atividade.peso,
        Nota.valor,
        Nota.realizada
    ).outerjoin(
        Nota, (Nota.atividade_id == Atividade.id) & (Nota.aluno_id == aluno_id)
    ).all()
    
    # Calcular média momentânea
    notas_ponderadas = [(a.valor * a.peso) for a in atividades_notas if a.valor is not None]
    pesos = [a.peso for a in atividades_notas if a.valor is not None]
    media_momentanea = sum(notas_ponderadas) / sum(pesos) if pesos else 0
    
    # Calcular chance de aprovação
    chance = calcular_chance_aprovacao(media_momentanea, atividades_notas)
    
    # Listar atividades não realizadas
    atividades_nao_realizadas = [
        {"id": a.id, "titulo": a.titulo, "valor_max": a.valor_max}
        for a in atividades_notas if a.realizada is False or (a.realizada is None and a.valor is None)
    ]
    
    # Listar atividades com notas baixas
    atividades_notas_baixas = [
        {"id": a.id, "titulo": a.titulo, "valor": a.valor, "valor_max": a.valor_max}
        for a in atividades_notas if a.valor is not None and a.valor < (a.valor_max * 0.7)
    ]
    
    resultado = {
        "aluno": {
            "id": aluno.id,
            "nome": aluno.nome
        },
        "media_momentanea": round(media_momentanea, 2),
        "chance_aprovacao": chance,
        "atividades_nao_realizadas": atividades_nao_realizadas,
        "atividades_notas_baixas": atividades_notas_baixas
    }
    
    return jsonify(resultado), 200

# --- Funções auxiliares ---

def calcular_categoria(media):
    """
    Calcula a categoria do aluno com base na média de notas.
    """
    if media is None:
        return {"nome": "Novato", "cor": "#CCCCCC", "icone": "novato.gif"}
    
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

def calcular_nivel(aluno_id):
    """
    Calcula o nível do aluno com base no XP total.
    """
    # Consulta para obter o total de XP (soma das notas)
    xp_total = db.session.query(func.sum(Nota.valor)).filter(Nota.aluno_id == aluno_id).scalar() or 0
    
    # Definição dos níveis
    if xp_total >= 1000:
        return {"nivel": 5, "titulo": "Desenvolvedor Sênior", "xp": xp_total, "proximo_nivel": None}
    elif xp_total >= 750:
        return {"nivel": 4, "titulo": "Desenvolvedor Pleno", "xp": xp_total, "proximo_nivel": 1000}
    elif xp_total >= 500:
        return {"nivel": 3, "titulo": "Desenvolvedor Júnior", "xp": xp_total, "proximo_nivel": 750}
    elif xp_total >= 250:
        return {"nivel": 2, "titulo": "Programador Iniciante", "xp": xp_total, "proximo_nivel": 500}
    else:
        return {"nivel": 1, "titulo": "Aprendiz de Código", "xp": xp_total, "proximo_nivel": 250}

def calcular_chance_aprovacao(media, atividades_notas):
    """
    Calcula a chance de aprovação com base na média atual e atividades pendentes.
    """
    # Contagem de atividades não realizadas
    atividades_nao_realizadas = sum(1 for a in atividades_notas if a.realizada is False or (a.realizada is None and a.valor is None))
    
    # Contagem de atividades com notas baixas
    atividades_notas_baixas = sum(1 for a in atividades_notas if a.valor is not None and a.valor < (a.valor_max * 0.7))
    
    # Cálculo base na média
    if media >= 90:
        chance_base = 95
    elif media >= 80:
        chance_base = 90
    elif media >= 70:
        chance_base = 80
    elif media >= 60:
        chance_base = 70
    elif media >= 50:
        chance_base = 50
    else:
        chance_base = 30
    
    # Ajustes com base em atividades não realizadas e notas baixas
    chance_final = chance_base - (atividades_nao_realizadas * 5) - (atividades_notas_baixas * 3)
    
    # Limitar entre 0 e 100
    chance_final = max(0, min(100, chance_final))
    
    # Gerar mensagem com base na chance
    if chance_final >= 90:
        mensagem = "Você está indo muito bem! Continue assim e a aprovação é praticamente garantida!"
    elif chance_final >= 70:
        mensagem = "Suas chances são boas, mas não relaxe! Mantenha o foco para garantir a aprovação."
    elif chance_final >= 50:
        mensagem = "Você está na corda bamba! Precisa se dedicar mais para garantir a aprovação."
    elif chance_final >= 30:
        mensagem = "Atenção! Suas chances estão baixas. É hora de correr atrás do prejuízo!"
    else:
        mensagem = "Situação crítica! Você precisa de uma reviravolta urgente para evitar a reprovação."
    
    return {
        "percentual": chance_final,
        "mensagem": mensagem,
        "atividades_nao_realizadas": atividades_nao_realizadas,
        "atividades_notas_baixas": atividades_notas_baixas
    }
