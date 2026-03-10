from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import User
from . import db
from .utils import admin_required, SENHA_PADRAO

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html")


@main_bp.route("/admin")
@login_required
@admin_required
def painel_admin():
    return render_template("dashboard.html")


@main_bp.route("/admin/users")
@login_required
@admin_required
def listar_usuarios():
    usuarios = User.query.all()
    return render_template("admin_users.html", usuarios=usuarios)


@main_bp.route("/admin/user/create", methods=["GET", "POST"])
@login_required
@admin_required
def criar_usuario():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        is_admin = request.form.get("is_admin") == "on"

        if not username or not password:
            flash("Usuário e senha são obrigatórios.")
            return redirect(url_for("main.criar_usuario"))

        if User.query.filter_by(username=username).first():
            flash("Usuário já existe.")
            return redirect(url_for("main.criar_usuario"))

        novo_usuario = User(
            username=username,
            is_admin=is_admin,
            must_change_password=True
        )
        novo_usuario.set_password(password)

        db.session.add(novo_usuario)
        db.session.commit()

        flash("Usuário criado com sucesso.")
        return redirect(url_for("main.listar_usuarios"))

    return render_template("admin_user_form.html", usuario=None, titulo="Criar Usuário")


@main_bp.route("/admin/user/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def editar_usuario(user_id):
    usuario = User.query.get_or_404(user_id)

    if request.method == "POST":
        username = request.form.get("username")
        is_admin = request.form.get("is_admin") == "on"
        nova_senha = request.form.get("password")

        if not username:
            flash("Usuário é obrigatório.")
            return redirect(url_for("main.editar_usuario", user_id=user_id))

        # Verifica se username já existe em outro usuário
        usuario_existente = User.query.filter_by(username=username).first()
        if usuario_existente and usuario_existente.id != user_id:
            flash("Nome de usuário já está em uso.")
            return redirect(url_for("main.editar_usuario", user_id=user_id))

        usuario.username = username
        usuario.is_admin = is_admin

        if nova_senha:
            usuario.set_password(nova_senha)
            usuario.must_change_password = True

        db.session.commit()

        flash("Usuário atualizado com sucesso.")
        return redirect(url_for("main.listar_usuarios"))

    return render_template("admin_user_form.html", usuario=usuario, titulo="Editar Usuário")


@main_bp.route("/admin/user/delete/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def excluir_usuario(user_id):
    usuario = User.query.get_or_404(user_id)

    if usuario.id == current_user.id:
        flash("Você não pode excluir seu próprio usuário.")
        return redirect(url_for("main.listar_usuarios"))

    db.session.delete(usuario)
    db.session.commit()

    flash("Usuário excluído com sucesso.")
    return redirect(url_for("main.listar_usuarios"))


@main_bp.route("/admin/reset-password/<int:user_id>")
@login_required
@admin_required
def resetar_senha(user_id):
    user = User.query.get_or_404(user_id)

    user.set_password(SENHA_PADRAO)
    user.must_change_password = True
    db.session.commit()

    flash(f"Senha redefinida para '{SENHA_PADRAO}'.")
    return redirect(url_for("main.listar_usuarios"))


@main_bp.route("/admin/toggle-user/<int:user_id>")
@login_required
@admin_required
def toggle_usuario(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("Você não pode bloquear seu próprio usuário.")
        return redirect(url_for("main.listar_usuarios"))

    user.is_active = not user.is_active
    db.session.commit()

    status = "ativado" if user.is_active else "bloqueado"
    flash(f"Usuário {status}.")
    return redirect(url_for("main.listar_usuarios"))


