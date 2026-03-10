
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from .models import User, TipoInstrumento, Naipe, FuncaoBanda
from . import db

SENHA_PADRAO = "123456"

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        if not current_user.is_admin:
            flash("Acesso restrito ao administrador.")
            return redirect(url_for("main.dashboard"))

        return f(*args, **kwargs)

    return decorated_function

def criar_admin_padrao():
    admin = User.query.filter_by(is_admin=True).first()

    if not admin:
        novo_admin = User(
            username="admin",
            is_admin=True,
            must_change_password=True
        )
        novo_admin.set_password(SENHA_PADRAO)

        db.session.add(novo_admin)
        db.session.commit()

def criar_dados_iniciais():
    """Cria dados iniciais para o sistema (tipos de instrumento, naipes, funções)"""
    
    # Criar tipos de instrumento se não existirem
    if not TipoInstrumento.query.first():
        tipos = [
            TipoInstrumento(nome="Sopro"),
            TipoInstrumento(nome="Percussão"),
            TipoInstrumento(nome="Metais"),
        ]
        db.session.add_all(tipos)
    
    # Criar naipes se não existirem
    if not Naipe.query.first():
        naipes = [
            Naipe(nome="Madeira"),
            Naipe(nome="Metais"),
            Naipe(nome="Percussão"),
            Naipe(nome="Clarim"),
        ]
        db.session.add_all(naipes)
    
    # Criar funções da banda se não existirem
    if not FuncaoBanda.query.first():
        funcoes = [
            FuncaoBanda(nome_funcao="Mestre"),
            FuncaoBanda(nome_funcao="Sub-Mestre"),
            FuncaoBanda(nome_funcao="Oficial deFileira"),
            FuncaoBanda(nome_funcao="Cabo deFileira"),
            FuncaoBanda(nome_funcao="Alferes"),
            FuncaoBanda(nome_funcao="Soldado"),
        ]
        db.session.add_all(funcoes)
    
    db.session.commit()

