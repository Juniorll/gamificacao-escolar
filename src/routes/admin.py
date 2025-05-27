from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.models.database import db, Professor, Configuracao

# Cria o blueprint
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/configuracoes')
@login_required
def configuracoes():
    return render_template('admin/configuracoes.html')

# Adicione aqui as outras rotas do admin
