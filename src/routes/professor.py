from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.models.database import db, Professor, Colegio, Turma, Disciplina, Periodo, Aluno, Atividade, Nota, TrabalhoExemplar

# Cria o blueprint
professor_bp = Blueprint('professor', __name__)

@professor_bp.route('/dashboard')
@login_required
def dashboard():
    # Contagem de registros para o dashboard
    alunos_count = Aluno.query.count()
    turmas_count = Turma.query.count()
    disciplinas_count = Disciplina.query.count()
    atividades_count = Atividade.query.count()
    
    return render_template('professor/dashboard.html', 
                          alunos_count=alunos_count,
                          turmas_count=turmas_count,
                          disciplinas_count=disciplinas_count,
                          atividades_count=atividades_count)

# Rotas para Colégios
@professor_bp.route('/colegios')
@login_required
def colegios():
    colegios = Colegio.query.all()
    return render_template('professor/colegios.html', colegios=colegios)

@professor_bp.route('/colegio/novo', methods=['GET', 'POST'])
@login_required
def colegio_novo():
    if request.method == 'POST':
        nome = request.form.get('nome')
        endereco = request.form.get('endereco')
        
        novo_colegio = Colegio(
            nome=nome,
            endereco=endereco
        )
        
        db.session.add(novo_colegio)
        db.session.commit()
        
        flash('Colégio cadastrado com sucesso!', 'success')
        return redirect(url_for('professor.colegios'))
    
    return render_template('professor/colegio_form.html')

@professor_bp.route('/colegio/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def colegio_editar(id):
    colegio = Colegio.query.get_or_404(id)
    
    if request.method == 'POST':
        colegio.nome = request.form.get('nome')
        colegio.endereco = request.form.get('endereco')
        
        db.session.commit()
        
        flash('Colégio atualizado com sucesso!', 'success')
        return redirect(url_for('professor.colegios'))
    
    return render_template('professor/colegio_form.html', colegio=colegio)

@professor_bp.route('/colegio/<int:id>/excluir', methods=['POST'])
@login_required
def colegio_excluir(id):
    colegio = Colegio.query.get_or_404(id)
    
    db.session.delete(colegio)
    db.session.commit()
    
    flash('Colégio excluído com sucesso!', 'success')
    return redirect(url_for('professor.colegios'))

# Rotas para Turmas
@professor_bp.route('/turmas')
@login_required
def turmas():
    turmas = Turma.query.all()
    return render_template('professor/turmas.html', turmas=turmas)

@professor_bp.route('/turma/nova', methods=['GET', 'POST'])
@login_required
def turma_nova():
    colegios = Colegio.query.all()
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        ano = request.form.get('ano')
        colegio_id = request.form.get('colegio_id')
        
        nova_turma = Turma(
            nome=nome,
            ano=ano,
            professor_id=current_user.id,
            colegio_id=colegio_id
        )
        
        db.session.add(nova_turma)
        db.session.commit()
        
        flash('Turma cadastrada com sucesso!', 'success')
        return redirect(url_for('professor.turmas'))
    
    return render_template('professor/turma_form.html', colegios=colegios)

@professor_bp.route('/turma/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def turma_editar(id):
    turma = Turma.query.get_or_404(id)
    colegios = Colegio.query.all()
    
    if request.method == 'POST':
        turma.nome = request.form.get('nome')
        turma.ano = request.form.get('ano')
        turma.colegio_id = request.form.get('colegio_id')
        
        db.session.commit()
        
        flash('Turma atualizada com sucesso!', 'success')
        return redirect(url_for('professor.turmas'))
    
    return render_template('professor/turma_form.html', turma=turma, colegios=colegios)

@professor_bp.route('/turma/<int:id>/excluir', methods=['POST'])
@login_required
def turma_excluir(id):
    turma = Turma.query.get_or_404(id)
    
    db.session.delete(turma)
    db.session.commit()
    
    flash('Turma excluída com sucesso!', 'success')
    return redirect(url_for('professor.turmas'))

# Rotas para Disciplinas
@professor_bp.route('/disciplinas')
@login_required
def disciplinas():
    disciplinas = Disciplina.query.filter_by(professor_id=current_user.id).all()
    return render_template('professor/disciplinas.html', disciplinas=disciplinas)

@professor_bp.route('/disciplina/nova', methods=['GET', 'POST'])
@login_required
def disciplina_nova():
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        icone = request.form.get('icone')
        cor = request.form.get('cor')
        
        nova_disciplina = Disciplina(
            nome=nome,
            descricao=descricao,
            professor_id=current_user.id,
            icone=icone,
            cor=cor
        )
        
        db.session.add(nova_disciplina)
        db.session.commit()
        
        flash('Disciplina cadastrada com sucesso!', 'success')
        return redirect(url_for('professor.disciplinas'))
    
    return render_template('professor/disciplina_form.html')

@professor_bp.route('/disciplina/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def disciplina_editar(id):
    disciplina = Disciplina.query.get_or_404(id)
    
    # Verificar se a disciplina pertence ao professor atual
    if disciplina.professor_id != current_user.id:
        flash('Você não tem permissão para editar esta disciplina.', 'danger')
        return redirect(url_for('professor.disciplinas'))
    
    if request.method == 'POST':
        disciplina.nome = request.form.get('nome')
        disciplina.descricao = request.form.get('descricao')
        disciplina.icone = request.form.get('icone')
        disciplina.cor = request.form.get('cor')
        
        db.session.commit()
        
        flash('Disciplina atualizada com sucesso!', 'success')
        return redirect(url_for('professor.disciplinas'))
    
    return render_template('professor/disciplina_form.html', disciplina=disciplina)

@professor_bp.route('/disciplina/<int:id>/excluir', methods=['POST'])
@login_required
def disciplina_excluir(id):
    disciplina = Disciplina.query.get_or_404(id)
    
    # Verificar se a disciplina pertence ao professor atual
    if disciplina.professor_id != current_user.id:
        flash('Você não tem permissão para excluir esta disciplina.', 'danger')
        return redirect(url_for('professor.disciplinas'))
    
    db.session.delete(disciplina)
    db.session.commit()
    
    flash('Disciplina excluída com sucesso!', 'success')
    return redirect(url_for('professor.disciplinas'))

# Rotas para Períodos
@professor_bp.route('/periodos')
@login_required
def periodos():
    periodos = Periodo.query.all()
    return render_template('professor/periodos.html', periodos=periodos)

@professor_bp.route('/periodo/novo', methods=['GET', 'POST'])
@login_required
def periodo_novo():
    periodos = Periodo.query.all()
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')
        tipo = request.form.get('tipo')
        periodo_pai_id = request.form.get('periodo_pai_id')
        
        novo_periodo = Periodo(
            nome=nome,
            data_inicio=data_inicio,
            data_fim=data_fim,
            tipo=tipo,
            periodo_pai_id=periodo_pai_id if periodo_pai_id else None
        )
        
        db.session.add(novo_periodo)
        db.session.commit()
        
        flash('Período cadastrado com sucesso!', 'success')
        return redirect(url_for('professor.periodos'))
    
    return render_template('professor/periodo_form.html', periodos=periodos)

@professor_bp.route('/periodo/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def periodo_editar(id):
    periodo = Periodo.query.get_or_404(id)
    periodos = Periodo.query.filter(Periodo.id != id).all()
    
    if request.method == 'POST':
        periodo.nome = request.form.get('nome')
        periodo.data_inicio = request.form.get('data_inicio')
        periodo.data_fim = request.form.get('data_fim')
        periodo.tipo = request.form.get('tipo')
        periodo_pai_id = request.form.get('periodo_pai_id')
        periodo.periodo_pai_id = periodo_pai_id if periodo_pai_id else None
        
        db.session.commit()
        
        flash('Período atualizado com sucesso!', 'success')
        return redirect(url_for('professor.periodos'))
    
    return render_template('professor/periodo_form.html', periodo=periodo, periodos=periodos)

@professor_bp.route('/periodo/<int:id>/excluir', methods=['POST'])
@login_required
def periodo_excluir(id):
    periodo = Periodo.query.get_or_404(id)
    
    db.session.delete(periodo)
    db.session.commit()
    
    flash('Período excluído com sucesso!', 'success')
    return redirect(url_for('professor.periodos'))

# Rotas para Alunos
@professor_bp.route('/alunos')
@login_required
def alunos():
    turmas = Turma.query.filter_by(professor_id=current_user.id).all()
    turma_ids = [turma.id for turma in turmas]
    alunos = Aluno.query.filter(Aluno.turma_id.in_(turma_ids)).all()
    colegios = Colegio.query.join(Turma).filter(Turma.professor_id == current_user.id).distinct().all()
    
    return render_template('professor/alunos.html', alunos=alunos, turmas=turmas, colegios=colegios)

@professor_bp.route('/alunos')
@login_required
def alunos():
    # Obter parâmetros de filtro
    turma_id = request.args.get('turma_id', type=int)
    
    # Consulta base para alunos
    query = Aluno.query
    
    # Aplicar filtros se fornecidos
    if turma_id:
        query = query.filter(Aluno.turma_id == turma_id)
    
    # Obter alunos
    alunos = query.all()
    
    # Obter turmas para filtro
    turmas = Turma.query.all()
    
    return render_template('professor/alunos.html', alunos=alunos, turmas=turmas)

@professor_bp.route('/aluno/importar', methods=['GET', 'POST'])
@login_required
def aluno_importar():
    turmas = Turma.query.filter_by(professor_id=current_user.id).all()
    
    if request.method == 'POST':
        # Lógica para importação de alunos
        # Aqui seria implementada a importação via CSV ou JSON
        
        flash('Alunos importados com sucesso!', 'success')
        return redirect(url_for('professor.alunos'))
    
    return render_template('professor/aluno_importar.html', turmas=turmas)

@professor_bp.route('/aluno/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def aluno_editar(id):
    aluno = Aluno.query.get_or_404(id)
    turmas = Turma.query.filter_by(professor_id=current_user.id).all()
    
    # Verificar se o aluno pertence a uma turma do professor atual
    turma_ids = [turma.id for turma in turmas]
    if aluno.turma_id not in turma_ids:
        flash('Você não tem permissão para editar este aluno.', 'danger')
        return redirect(url_for('professor.alunos'))
    
    if request.method == 'POST':
        aluno.nome = request.form.get('nome')
        aluno.email = request.form.get('email')
        aluno.foto = request.form.get('foto')
        aluno.avatar = request.form.get('avatar')
        aluno.turma_id = request.form.get('turma_id')
        
        db.session.commit()
        
        flash('Aluno atualizado com sucesso!', 'success')
        return redirect(url_for('professor.alunos'))
    
    return render_template('professor/aluno_form.html', aluno=aluno, turmas=turmas)

@professor_bp.route('/aluno/<int:id>/excluir', methods=['POST'])
@login_required
def aluno_excluir(id):
    aluno = Aluno.query.get_or_404(id)
    
    # Verificar se o aluno pertence a uma turma do professor atual
    turmas = Turma.query.filter_by(professor_id=current_user.id).all()
    turma_ids = [turma.id for turma in turmas]
    if aluno.turma_id not in turma_ids:
        flash('Você não tem permissão para excluir este aluno.', 'danger')
        return redirect(url_for('professor.alunos'))
    
    db.session.delete(aluno)
    db.session.commit()
    
    flash('Aluno excluído com sucesso!', 'success')
    return redirect(url_for('professor.alunos'))

# Rotas para Atividades
@professor_bp.route('/atividades')
@login_required
def atividades():
    # Obter parâmetros de filtro
    turma_id = request.args.get('turma_id', type=int)
    disciplina_id = request.args.get('disciplina_id', type=int)
    periodo_id = request.args.get('periodo_id', type=int)
    
    # Consulta base para atividades
    query = Atividade.query
    
    # Aplicar filtros se fornecidos
    if turma_id:
        query = query.filter(Atividade.turma_id == turma_id)
    if disciplina_id:
        query = query.filter(Atividade.disciplina_id == disciplina_id)
    if periodo_id:
        query = query.filter(Atividade.periodo_id == periodo_id)
    
    # Obter atividades
    atividades = query.all()
    
    # Obter dados para os filtros
    turmas = Turma.query.all()
    disciplinas = Disciplina.query.all()
    periodos = Periodo.query.all()
    
    return render_template('professor/atividades.html', 
                          atividades=atividades,
                          turmas=turmas,
                          disciplinas=disciplinas,
                          periodos=periodos)

@professor_bp.route('/atividade/nova', methods=['GET', 'POST'])
@login_required
def atividade_nova():
    disciplinas = Disciplina.query.filter_by(professor_id=current_user.id).all()
    periodos = Periodo.query.all()
    
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        tipo = request.form.get('tipo')
        valor_max = request.form.get('valor_max')
        peso = request.form.get('peso')
        data_entrega = request.form.get('data_entrega')
        disciplina_id = request.form.get('disciplina_id')
        periodo_id = request.form.get('periodo_id')
        
        nova_atividade = Atividade(
            titulo=titulo,
            descricao=descricao,
            tipo=tipo,
            valor_max=valor_max,
            peso=peso,
            data_entrega=data_entrega,
            professor_id=current_user.id,
            disciplina_id=disciplina_id,
            periodo_id=periodo_id
        )
        
        db.session.add(nova_atividade)
        db.session.commit()
        
        flash('Atividade cadastrada com sucesso!', 'success')
        return render_template('professor/atividade_form.html', 
                          turmas=turmas,
                          disciplinas=disciplinas,
                          periodos=periodos)

@professor_bp.route('/atividade/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def atividade_editar(id):
    atividade = Atividade.query.get_or_404(id)
    
    # Verificar se a atividade pertence ao professor atual
    if atividade.professor_id != current_user.id:
        flash('Você não tem permissão para editar esta atividade.', 'danger')
        return redirect(url_for('professor.atividades'))
    
    disciplinas = Disciplina.query.filter_by(professor_id=current_user.id).all()
    periodos = Periodo.query.all()
    
    if request.method == 'POST':
        atividade.titulo = request.form.get('titulo')
        atividade.descricao = request.form.get('descricao')
        atividade.tipo = request.form.get('tipo')
        atividade.valor_max = request.form.get('valor_max')
        atividade.peso = request.form.get('peso')
        atividade.data_entrega = request.form.get('data_entrega')
        atividade.disciplina_id = request.form.get('disciplina_id')
        atividade.periodo_id = request.form.get('periodo_id')
        
        db.session.commit()
        
        flash('Atividade atualizada com sucesso!', 'success')
        return redirect(url_for('professor.atividades'))
    
    return render_template('professor/atividade_form.html', atividade=atividade, disciplinas=disciplinas, periodos=periodos)

@professor_bp.route('/atividade/<int:id>/excluir', methods=['POST'])
@login_required
def atividade_excluir(id):
    atividade = Atividade.query.get_or_404(id)
    
    # Verificar se a atividade pertence ao professor atual
    if atividade.professor_id != current_user.id:
        flash('Você não tem permissão para excluir esta atividade.', 'danger')
        return redirect(url_for('professor.atividades'))
    
    db.session.delete(atividade)
    db.session.commit()
    
    flash('Atividade excluída com sucesso!', 'success')
    return redirect(url_for('professor.atividades'))

# Rotas para Notas
@professor_bp.route('/notas')
@login_required
def notas():
    # Obter parâmetros de filtro
    turma_id = request.args.get('turma_id', type=int)
    disciplina_id = request.args.get('disciplina_id', type=int)
    periodo_id = request.args.get('periodo_id', type=int)
    
    # Obter atividades para lançamento de notas
    query = Atividade.query
    
    # Aplicar filtros se fornecidos
    if turma_id:
        query = query.filter(Atividade.turma_id == turma_id)
    if disciplina_id:
        query = query.filter(Atividade.disciplina_id == disciplina_id)
    if periodo_id:
        query = query.filter(Atividade.periodo_id == periodo_id)
    
    # Obter atividades
    atividades = query.all()
    
    # Obter dados para os filtros
    turmas = Turma.query.all()
    disciplinas = Disciplina.query.all()
    periodos = Periodo.query.all()
    
    return render_template('professor/notas.html', 
                          atividades=atividades,
                          turmas=turmas,
                          disciplinas=disciplinas,
                          periodos=periodos)

@professor_bp.route('/nota/nova', methods=['GET', 'POST'])
@login_required
def nota_nova():
    disciplinas = Disciplina.query.filter_by(professor_id=current_user.id).all()
    disciplina_ids = [disciplina.id for disciplina in disciplinas]
    atividades = Atividade.query.filter(Atividade.disciplina_id.in_(disciplina_ids)).all()
    
    # Obter alunos das turmas do professor
    turmas = Turma.query.filter_by(professor_id=current_user.id).all()
    turma_ids = [turma.id for turma in turmas]
    alunos = Aluno.query.filter(Aluno.turma_id.in_(turma_ids)).all()
    
    if request.method == 'POST':
        aluno_id = request.form.get('aluno_id')
        atividade_id = request.form.get('atividade_id')
        valor = request.form.get('valor')
        realizada = 'realizada' in request.form
        
        nova_nota = Nota(
            aluno_id=aluno_id,
            atividade_id=atividade_id,
            valor=valor,
            realizada=realizada
        )
        
        db.session.add(nova_nota)
        db.session.commit()
        
        flash('Nota cadastrada com sucesso!', 'success')
        return redirect(url_for('professor.notas'))
    
    return render_template('professor/nota_form.html', atividades=atividades, alunos=alunos)

@professor_bp.route('/nota/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def nota_editar(id):
    nota = Nota.query.get_or_404(id)
    
    # Verificar se a nota pertence a uma atividade do professor atual
    atividade = Atividade.query.get(nota.atividade_id)
    if atividade.professor_id != current_user.id:
        flash('Você não tem permissão para editar esta nota.', 'danger')
        return redirect(url_for('professor.notas'))
    
    disciplinas = Disciplina.query.filter_by(professor_id=current_user.id).all()
    disciplina_ids = [disciplina.id for disciplina in disciplinas]
    atividades = Atividade.query.filter(Atividade.disciplina_id.in_(disciplina_ids)).all()
    
    # Obter alunos das turmas do professor
    turmas = Turma.query.filter_by(professor_id=current_user.id).all()
    turma_ids = [turma.id for turma in turmas]
    alunos = Aluno.query.filter(Aluno.turma_id.in_(turma_ids)).all()
    
    if request.method == 'POST':
        nota.aluno_id = request.form.get('aluno_id')
        nota.atividade_id = request.form.get('atividade_id')
        nota.valor = request.form.get('valor')
        nota.realizada = 'realizada' in request.form
        
        db.session.commit()
        
        flash('Nota atualizada com sucesso!', 'success')
        return redirect(url_for('professor.notas'))
    
    return render_template('professor/nota_form.html', nota=nota, atividades=atividades, alunos=alunos)

@professor_bp.route('/nota/<int:id>/excluir', methods=['POST'])
@login_required
def nota_excluir(id):
    nota = Nota.query.get_or_404(id)
    
    # Verificar se a nota pertence a uma atividade do professor atual
    atividade = Atividade.query.get(nota.atividade_id)
    if atividade.professor_id != current_user.id:
        flash('Você não tem permissão para excluir esta nota.', 'danger')
        return redirect(url_for('professor.notas'))
    
    db.session.delete(nota)
    db.session.commit()
    
    flash('Nota excluída com sucesso!', 'success')
    return redirect(url_for('professor.notas'))

# Rotas para Trabalhos Exemplares
@professor_bp.route('/trabalhos')
@login_required
def trabalhos():
    # Obter parâmetros de filtro
    turma_id = request.args.get('turma_id', type=int)
    disciplina_id = request.args.get('disciplina_id', type=int)
    periodo_id = request.args.get('periodo_id', type=int)
    
    # Obter trabalhos exemplares
    query = Trabalho.query
    
    # Aplicar filtros se fornecidos
    if turma_id:
        query = query.filter(Trabalho.turma_id == turma_id)
    if disciplina_id:
        query = query.filter(Trabalho.disciplina_id == disciplina_id)
    if periodo_id:
        query = query.filter(Trabalho.periodo_id == periodo_id)
    
    # Obter trabalhos
    trabalhos = query.all()
    
    # Obter dados para os filtros
    turmas = Turma.query.all()
    disciplinas = Disciplina.query.all()
    periodos = Periodo.query.all()
    
    return render_template('professor/trabalhos.html', 
                          trabalhos=trabalhos,
                          turmas=turmas,
                          disciplinas=disciplinas,
                          periodos=periodos)

@professor_bp.route('/trabalho/novo', methods=['GET', 'POST'])
@login_required
def trabalho_novo():
    disciplinas = Disciplina.query.filter_by(professor_id=current_user.id).all()
    disciplina_ids = [disciplina.id for disciplina in disciplinas]
    atividades = Atividade.query.filter(Atividade.disciplina_id.in_(disciplina_ids)).all()
    
    # Obter alunos das turmas do professor
    turmas = Turma.query.filter_by(professor_id=current_user.id).all()
    turma_ids = [turma.id for turma in turmas]
    alunos = Aluno.query.filter(Aluno.turma_id.in_(turma_ids)).all()
    
    if request.method == 'POST':
        aluno_id = request.form.get('aluno_id')
        atividade_id = request.form.get('atividade_id')
        descricao = request.form.get('descricao')
        link = request.form.get('link')
        arquivo = request.form.get('arquivo')
        
        novo_trabalho = TrabalhoExemplar(
            aluno_id=aluno_id,
            atividade_id=atividade_id,
            descricao=descricao,
            link=link,
            arquivo=arquivo
        )
        
        db.session.add(novo_trabalho)
        db.session.commit()
        
        flash('Trabalho exemplar cadastrado com sucesso!', 'success')
        return redirect(url_for('professor.trabalhos'))
    
    return render_template('professor/trabalho_form.html', atividades=atividades, alunos=alunos)

@professor_bp.route('/trabalho/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def trabalho_editar(id):
    trabalho = TrabalhoExemplar.query.get_or_404(id)
    
    # Verificar se o trabalho pertence a uma atividade do professor atual
    atividade = Atividade.query.get(trabalho.atividade_id)
    if atividade.professor_id != current_user.id:
        flash('Você não tem permissão para editar este trabalho exemplar.', 'danger')
        return redirect(url_for('professor.trabalhos'))
    
    disciplinas = Disciplina.query.filter_by(professor_id=current_user.id).all()
    disciplina_ids = [disciplina.id for disciplina in disciplinas]
    atividades = Atividade.query.filter(Atividade.disciplina_id.in_(disciplina_ids)).all()
    
    # Obter alunos das turmas do professor
    turmas = Turma.query.filter_by(professor_id=current_user.id).all()
    turma_ids = [turma.id for turma in turmas]
    alunos = Aluno.query.filter(Aluno.turma_id.in_(turma_ids)).all()
    
    if request.method == 'POST':
        trabalho.aluno_id = request.form.get('aluno_id')
        trabalho.atividade_id = request.form.get('atividade_id')
        trabalho.descricao = request.form.get('descricao')
        trabalho.link = request.form.get('link')
        trabalho.arquivo = request.form.get('arquivo')
        
        db.session.commit()
        
        flash('Trabalho exemplar atualizado com sucesso!', 'success')
        return redirect(url_for('professor.trabalhos'))
    
    return render_template('professor/trabalho_form.html', trabalho=trabalho, atividades=atividades, alunos=alunos)

@professor_bp.route('/trabalho/<int:id>/excluir', methods=['POST'])
@login_required
def trabalho_excluir(id):
    trabalho = TrabalhoExemplar.query.get_or_404(id)
    
    # Verificar se o trabalho pertence a uma atividade do professor atual
    atividade = Atividade.query.get(trabalho.atividade_id)
    if atividade.professor_id != current_user.id:
        flash('Você não tem permissão para excluir este trabalho exemplar.', 'danger')
        return redirect(url_for('professor.trabalhos'))
    
    db.session.delete(trabalho)
    db.session.commit()
    
    flash('Trabalho exemplar excluído com sucesso!', 'success')
    return redirect(url_for('professor.trabalhos'))

# Rota para Configurações
@professor_bp.route('/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    if request.method == 'POST':
        # Lógica para salvar configurações
        flash('Configurações salvas com sucesso!', 'success')
        return redirect(url_for('professor.configuracoes'))
    
    return render_template('professor/configuracoes.html')
