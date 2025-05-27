"""
Módulo de rotas para funcionalidades do professor.
Este arquivo contém as rotas para gerenciar colégios, turmas, disciplinas, períodos, alunos e atividades.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from src.models.database import db, Professor, Colegio, Turma, Disciplina, Periodo, Aluno, Atividade, Nota, TrabalhoExemplar
from werkzeug.utils import secure_filename
import os

# Criação do blueprint do professor
professor_bp = Blueprint("professor", __name__)

# --- Gerenciamento de Colégios ---

@professor_bp.route("/colegios", methods=["POST"])
@login_required
def criar_colegio():
    """Cria um novo colégio associado ao professor logado."""
    data = request.get_json()
    if not data or not data.get("nome"):
        return jsonify({"mensagem": "Nome do colégio é obrigatório"}), 400

    novo_colegio = Colegio(nome=data["nome"], endereco=data.get("endereco"))
    novo_colegio.professores.append(current_user)
    db.session.add(novo_colegio)
    db.session.commit()
    return jsonify({"mensagem": "Colégio criado com sucesso", "colegio": {"id": novo_colegio.id, "nome": novo_colegio.nome}}), 201

@professor_bp.route("/colegios", methods=["GET"])
@login_required
def listar_colegios():
    """Lista os colégios associados ao professor logado."""
    colegios = current_user.colegios
    return jsonify([{"id": c.id, "nome": c.nome, "endereco": c.endereco} for c in colegios]), 200

# --- Gerenciamento de Turmas ---

@professor_bp.route("/turmas", methods=["POST"])
@login_required
def criar_turma():
    """Cria uma nova turma associada a um colégio do professor."""
    data = request.get_json()
    if not data or not data.get("nome") or not data.get("ano") or not data.get("colegio_id"):
        return jsonify({"mensagem": "Nome, ano e ID do colégio são obrigatórios"}), 400

    colegio = Colegio.query.filter_by(id=data["colegio_id"]).first()
    # Verifica se o colégio existe e pertence ao professor
    if not colegio or current_user not in colegio.professores:
        return jsonify({"mensagem": "Colégio inválido ou não pertence ao professor"}), 403

    nova_turma = Turma(nome=data["nome"], ano=data["ano"], colegio_id=data["colegio_id"], professor_id=current_user.id)
    db.session.add(nova_turma)
    db.session.commit()
    return jsonify({"mensagem": "Turma criada com sucesso", "turma": {"id": nova_turma.id, "nome": nova_turma.nome}}), 201

@professor_bp.route("/turmas", methods=["GET"])
@login_required
def listar_turmas():
    """Lista as turmas criadas pelo professor logado."""
    turmas = Turma.query.filter_by(professor_id=current_user.id).all()
    return jsonify([{"id": t.id, "nome": t.nome, "ano": t.ano, "colegio_id": t.colegio_id} for t in turmas]), 200

# --- Gerenciamento de Disciplinas ---

@professor_bp.route("/disciplinas", methods=["POST"])
@login_required
def criar_disciplina():
    """Cria uma nova disciplina associada ao professor."""
    data = request.get_json()
    if not data or not data.get("nome"):
        return jsonify({"mensagem": "Nome da disciplina é obrigatório"}), 400

    nova_disciplina = Disciplina(
        nome=data["nome"],
        descricao=data.get("descricao"),
        professor_id=current_user.id,
        cor=data.get("cor", "#3498db")
    )
    db.session.add(nova_disciplina)
    db.session.commit()
    return jsonify({"mensagem": "Disciplina criada com sucesso", "disciplina": {"id": nova_disciplina.id, "nome": nova_disciplina.nome}}), 201

@professor_bp.route("/disciplinas", methods=["GET"])
@login_required
def listar_disciplinas():
    """Lista as disciplinas criadas pelo professor logado."""
    disciplinas = Disciplina.query.filter_by(professor_id=current_user.id).all()
    return jsonify([{"id": d.id, "nome": d.nome, "descricao": d.descricao, "cor": d.cor} for d in disciplinas]), 200

# --- Gerenciamento de Períodos ---

@professor_bp.route("/periodos", methods=["POST"])
@login_required
def criar_periodo():
    """Cria um novo período letivo."""
    data = request.get_json()
    if not data or not data.get("nome") or not data.get("data_inicio") or not data.get("data_fim") or not data.get("tipo"):
        return jsonify({"mensagem": "Nome, data de início, data de fim e tipo são obrigatórios"}), 400

    # TODO: Validar formato das datas
    novo_periodo = Periodo(
        nome=data["nome"],
        data_inicio=data["data_inicio"],
        data_fim=data["data_fim"],
        tipo=data["tipo"],
        periodo_pai_id=data.get("periodo_pai_id")
    )
    db.session.add(novo_periodo)
    db.session.commit()
    return jsonify({"mensagem": "Período criado com sucesso", "periodo": {"id": novo_periodo.id, "nome": novo_periodo.nome}}), 201

@professor_bp.route("/periodos", methods=["GET"])
@login_required
def listar_periodos():
    """Lista os períodos cadastrados."""
    # Idealmente, filtrar por períodos relevantes ao professor, mas por enquanto lista todos
    periodos = Periodo.query.order_by(Periodo.data_inicio.desc()).all()
    # TODO: Implementar estrutura hierárquica na resposta
    return jsonify([{
        "id": p.id, 
        "nome": p.nome, 
        "tipo": p.tipo, 
        "data_inicio": p.data_inicio.isoformat(), 
        "data_fim": p.data_fim.isoformat(),
        "periodo_pai_id": p.periodo_pai_id
    } for p in periodos]), 200

# --- Gerenciamento de Alunos ---

@professor_bp.route("/alunos", methods=["POST"])
@login_required
def criar_aluno():
    """Cria um novo aluno associado a uma turma do professor."""
    data = request.form # Usar request.form para lidar com upload de arquivos
    if not data or not data.get("nome") or not data.get("turma_id"):
        return jsonify({"mensagem": "Nome e ID da turma são obrigatórios"}), 400

    turma = Turma.query.filter_by(id=data["turma_id"], professor_id=current_user.id).first()
    if not turma:
        return jsonify({"mensagem": "Turma inválida ou não pertence ao professor"}), 403

    foto_path = None
    avatar_path = None
    # TODO: Implementar lógica de upload de foto/avatar

    novo_aluno = Aluno(
        nome=data["nome"],
        email=data.get("email"),
        turma_id=data["turma_id"],
        foto=foto_path,
        avatar=avatar_path
    )
    db.session.add(novo_aluno)
    db.session.commit()
    return jsonify({"mensagem": "Aluno criado com sucesso", "aluno": {"id": novo_aluno.id, "nome": novo_aluno.nome}}), 201

@professor_bp.route("/turmas/<int:turma_id>/alunos", methods=["GET"])
@login_required
def listar_alunos_por_turma(turma_id):
    """Lista os alunos de uma turma específica do professor."""
    turma = Turma.query.filter_by(id=turma_id, professor_id=current_user.id).first()
    if not turma:
        return jsonify({"mensagem": "Turma inválida ou não pertence ao professor"}), 403

    alunos = Aluno.query.filter_by(turma_id=turma_id).all()
    return jsonify([{
        "id": a.id, 
        "nome": a.nome, 
        "email": a.email, 
        "foto": a.foto, 
        "avatar": a.avatar
    } for a in alunos]), 200

# --- Gerenciamento de Atividades ---

@professor_bp.route("/atividades", methods=["POST"])
@login_required
def criar_atividade():
    """Cria uma nova atividade associada a uma disciplina e período."""
    data = request.get_json()
    required_fields = ["titulo", "tipo", "valor_max", "data_entrega", "disciplina_id", "periodo_id"]
    if not data or not all(field in data for field in required_fields):
        return jsonify({"mensagem": f"Campos obrigatórios ausentes: {', '.join(required_fields)}"}), 400

    # Verifica se a disciplina pertence ao professor
    disciplina = Disciplina.query.filter_by(id=data["disciplina_id"], professor_id=current_user.id).first()
    if not disciplina:
        return jsonify({"mensagem": "Disciplina inválida ou não pertence ao professor"}), 403
        
    # Verifica se o período existe
    periodo = Periodo.query.get(data["periodo_id"])
    if not periodo:
        return jsonify({"mensagem": "Período inválido"}), 400

    # TODO: Validar formato da data_entrega
    nova_atividade = Atividade(
        titulo=data["titulo"],
        descricao=data.get("descricao"),
        tipo=data["tipo"],
        valor_max=data["valor_max"],
        peso=data.get("peso", 1.0),
        data_entrega=data["data_entrega"],
        professor_id=current_user.id,
        disciplina_id=data["disciplina_id"],
        periodo_id=data["periodo_id"]
    )
    db.session.add(nova_atividade)
    db.session.commit()
    return jsonify({"mensagem": "Atividade criada com sucesso", "atividade": {"id": nova_atividade.id, "titulo": nova_atividade.titulo}}), 201

@professor_bp.route("/atividades", methods=["GET"])
@login_required
def listar_atividades():
    """Lista as atividades criadas pelo professor logado."""
    # TODO: Adicionar filtros por disciplina, período, etc.
    atividades = Atividade.query.filter_by(professor_id=current_user.id).order_by(Atividade.data_entrega.desc()).all()
    return jsonify([{
        "id": a.id,
        "titulo": a.titulo,
        "tipo": a.tipo,
        "valor_max": a.valor_max,
        "peso": a.peso,
        "data_entrega": a.data_entrega.isoformat(),
        "disciplina_id": a.disciplina_id,
        "periodo_id": a.periodo_id
    } for a in atividades]), 200

# --- Lançamento de Notas ---

@professor_bp.route("/notas", methods=["POST"])
@login_required
def lancar_nota():
    """Lança ou atualiza a nota de um aluno em uma atividade."""
    data = request.get_json()
    if not data or not data.get("aluno_id") or not data.get("atividade_id") or "valor" not in data:
        return jsonify({"mensagem": "ID do aluno, ID da atividade e valor são obrigatórios"}), 400

    aluno = Aluno.query.get(data["aluno_id"])
    atividade = Atividade.query.filter_by(id=data["atividade_id"], professor_id=current_user.id).first()

    if not aluno:
        return jsonify({"mensagem": "Aluno não encontrado"}), 404
    if not atividade:
        return jsonify({"mensagem": "Atividade inválida ou não pertence ao professor"}), 403
    # TODO: Verificar se o aluno pertence a uma turma gerenciada pelo professor?

    nota_existente = Nota.query.filter_by(aluno_id=data["aluno_id"], atividade_id=data["atividade_id"]).first()

    realizada = data.get("realizada", True if data["valor"] is not None else False)

    if nota_existente:
        nota_existente.valor = data["valor"]
        nota_existente.realizada = realizada
    else:
        nova_nota = Nota(
            aluno_id=data["aluno_id"],
            atividade_id=data["atividade_id"],
            valor=data["valor"],
            realizada=realizada
        )
        db.session.add(nova_nota)
    
    # Lógica para marcar trabalho como exemplar automaticamente
    if data["valor"] is not None and data["valor"] >= 90 and atividade.tipo != 'trabalho_exemplar':
        trabalho_exemplar_existente = TrabalhoExemplar.query.filter_by(aluno_id=data["aluno_id"], atividade_id=data["atividade_id"]).first()
        if not trabalho_exemplar_existente:
            novo_trabalho_exemplar = TrabalhoExemplar(
                aluno_id=data["aluno_id"],
                atividade_id=data["atividade_id"],
                descricao=f"Trabalho exemplar da atividade: {atividade.titulo}"
            )
            db.session.add(novo_trabalho_exemplar)

    db.session.commit()
    return jsonify({"mensagem": "Nota lançada/atualizada com sucesso"}), 200

# --- Trabalhos Exemplares ---

@professor_bp.route("/trabalhos_exemplares", methods=["POST"])
@login_required
def marcar_trabalho_exemplar():
    """Marca manualmente um trabalho como exemplar."""
    data = request.get_json()
    if not data or not data.get("aluno_id") or not data.get("atividade_id"):
        return jsonify({"mensagem": "ID do aluno e ID da atividade são obrigatórios"}), 400

    aluno = Aluno.query.get(data["aluno_id"])
    atividade = Atividade.query.filter_by(id=data["atividade_id"], professor_id=current_user.id).first()

    if not aluno:
        return jsonify({"mensagem": "Aluno não encontrado"}), 404
    if not atividade:
        return jsonify({"mensagem": "Atividade inválida ou não pertence ao professor"}), 403

    trabalho_exemplar_existente = TrabalhoExemplar.query.filter_by(aluno_id=data["aluno_id"], atividade_id=data["atividade_id"]).first()
    if trabalho_exemplar_existente:
        return jsonify({"mensagem": "Este trabalho já foi marcado como exemplar"}), 400

    novo_trabalho_exemplar = TrabalhoExemplar(
        aluno_id=data["aluno_id"],
        atividade_id=data["atividade_id"],
        descricao=data.get("descricao", f"Trabalho exemplar da atividade: {atividade.titulo}"),
        link=data.get("link"),
        arquivo=data.get("arquivo") # TODO: Implementar upload de arquivo
    )
    db.session.add(novo_trabalho_exemplar)
    db.session.commit()
    return jsonify({"mensagem": "Trabalho marcado como exemplar com sucesso"}), 201

# TODO: Adicionar rotas para PUT/DELETE (atualizar/excluir) para Colégios, Turmas, Disciplinas, Períodos, Alunos, Atividades
# TODO: Implementar funcionalidade de importação de dados
# TODO: Implementar funcionalidade de personalização (upload de logos, ícones, gifs)

