from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.models.database import db, Professor, Configuracao

# Cria o blueprint
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        # Atualizar configurações
        for chave in request.form:
            if chave.startswith('config_'):
                config_chave = chave.replace('config_', '')
                config_valor = request.form[chave]
                
                # Verificar se a configuração já existe
                config = Configuracao.query.filter_by(chave=config_chave).first()
                
                if config:
                    config.valor = config_valor
                else:
                    nova_config = Configuracao(
                        chave=config_chave,
                        valor=config_valor,
                        descricao=f"Configuração {config_chave}"
                    )
                    db.session.add(nova_config)
        
        db.session.commit()
        flash('Configurações atualizadas com sucesso!', 'success')
        return redirect(url_for('admin.configuracoes'))
    
    # Obter todas as configurações
    configuracoes = Configuracao.query.all()
    
    return render_template('admin/configuracoes.html', configuracoes=configuracoes)
