from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .models import User, Aluno, Escola, Instrumento, TipoInstrumento, Naipe, FuncaoBanda, Responsavel, Uniforme, AlunoInstrumento, AlunoEscola, Logradouro, Cidade
from . import db
from .utils import admin_required, SENHA_PADRAO
from datetime import datetime
import os
from werkzeug.utils import secure_filename

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


# ========================
# ROTAS PARA GESTÃO DE ALUNOS (INTEGRANTES DA BANDA)
# ========================

@main_bp.route("/admin/alunos")
@login_required
@admin_required
def listar_alunos():
    """Lista todos os alunos com filtros opcionais"""
    # Filtros
    nome_busca = request.args.get('busca', '')
    ativo_filter = request.args.get('ativo', '')
    
    query = Aluno.query
    
    if nome_busca:
        query = query.filter(Aluno.nome.ilike(f'%{nome_busca}%'))
    
    if ativo_filter == '1':
        query = query.filter(Aluno.ativo == True)
    elif ativo_filter == '0':
        query = query.filter(Aluno.ativo == False)
    
    alunos = query.order_by(Aluno.nome).all()
    
    return render_template("admin_alunos.html", 
                           alunos=alunos, 
                           busca=nome_busca, 
                           ativo_filter=ativo_filter)


@main_bp.route("/admin/aluno/create", methods=["GET", "POST"])
@login_required
@admin_required
def criar_aluno():
    """Cria um novo aluno (integrante da banda)"""
    # Dados para os selects do formulário
    escolas = Escola.query.all()
    instrumentos = Instrumento.query.filter_by(ativo=True).all()
    tipos_instrumento = TipoInstrumento.query.all()
    naipes = Naipe.query.all()
    
    if request.method == "POST":
        # Dados pessoais do aluno
        nome = request.form.get("nome")
        data_nascimento = request.form.get("data_nascimento")
        naturalidade = request.form.get("naturalidade")
        cin_rg = request.form.get("cin_rg")
        uid_vt = request.form.get("uid_vt")
        email = request.form.get("email")
        telefone = request.form.get("telefone")
        cep = request.form.get("cep")
        endereco = request.form.get("endereco")
        bairro = request.form.get("bairro")
        cidade = request.form.get("cidade")
        estado = request.form.get("estado")
        
        if not nome:
            flash("Nome é obrigatório.")
            return redirect(url_for("main.criar_aluno"))
        
        # Verificar RG único
        if cin_rg and Aluno.query.filter_by(cin_rg=cin_rg).first():
            flash("RG já cadastrado.")
            return redirect(url_for("main.criar_aluno"))
        
        # Verificar UID VT único
        if uid_vt and Aluno.query.filter_by(uid_vt=uid_vt).first():
            flash("UID VT já cadastrado.")
            return redirect(url_for("main.criar_aluno"))
        
        # Converter data de nascimento
        data_nasc = None
        if data_nascimento:
            try:
                data_nasc = datetime.strptime(data_nascimento, '%Y-%m-%d').date()
            except ValueError:
                flash("Data de nascimento inválida.")
                return redirect(url_for("main.criar_aluno"))
        
        # Criar aluno
        novo_aluno = Aluno(
            nome=nome,
            data_nascimento=data_nasc,
            naturalidade=naturalidade,
            cin_rg=cin_rg,
            uid_vt=uid_vt,
            email=email,
            telefone=telefone,
            cep=cep,
            endereco=endereco,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            ativo=True
        )
        db.session.add(novo_aluno)
        db.session.flush()  # Para obter o ID do aluno
        
        # Processar upload de foto
        foto = request.files.get('foto')
        if foto and foto.filename:
            foto_path = salvar_foto_aluno(foto, novo_aluno.id)
            if foto_path:
                novo_aluno.foto_path = foto_path
        
        # Dados do responsável
        nome_pai = request.form.get("nome_pai")
        nome_mae = request.form.get("nome_mae")
        telefone_responsavel = request.form.get("telefone_responsavel")
        email_responsavel = request.form.get("email_responsavel")
        endereco_responsavel = request.form.get("endereco_responsavel")
        
        if nome_pai or nome_mae or telefone_responsavel:
            responsavel = Responsavel(
                aluno_id=novo_aluno.id,
                nome_pai=nome_pai,
                nome_mae=nome_mae,
                telefone=telefone_responsavel,
                email=email_responsavel,
                endereco=endereco_responsavel
            )
            db.session.add(responsavel)
        
        # Escola
        escola_id = request.form.get("escola_id")
        if escola_id:
            aluno_escola = AlunoEscola(
                aluno_id=novo_aluno.id,
                escola_id=int(escola_id)
            )
            db.session.add(aluno_escola)
        
        db.session.commit()
        
        flash("Aluno criado com sucesso!")
        return redirect(url_for("main.listar_alunos"))
    
    return render_template("admin_aluno_form.html",
                           aluno=None,
                           titulo="Novo Integrante",
                           escolas=escolas,
                           instrumentos=instrumentos,
                           tipos_instrumento=tipos_instrumento,
                           naipes=naipes)


@main_bp.route("/admin/aluno/edit/<int:aluno_id>", methods=["GET", "POST"])
@login_required
@admin_required
def editar_aluno(aluno_id):
    """Edita um aluno existente"""
    aluno = Aluno.query.get_or_404(aluno_id)
    
    # Dados para os selects do formulário
    escolas = Escola.query.all()
    instrumentos = Instrumento.query.filter_by(ativo=True).all()
    tipos_instrumento = TipoInstrumento.query.all()
    naipes = Naipe.query.all()
    
    if request.method == "POST":
        # Dados pessoais do aluno
        nome = request.form.get("nome")
        data_nascimento = request.form.get("data_nascimento")
        naturalidade = request.form.get("naturalidade")
        cin_rg = request.form.get("cin_rg")
        uid_vt = request.form.get("uid_vt")
        email = request.form.get("email")
        telefone = request.form.get("telefone")
        cep = request.form.get("cep")
        endereco = request.form.get("endereco")
        bairro = request.form.get("bairro")
        cidade = request.form.get("cidade")
        estado = request.form.get("estado")
        
        if not nome:
            flash("Nome é obrigatório.")
            return redirect(url_for("main.editar_aluno", aluno_id=aluno_id))
        
        # Verificar RG único (exceto o próprio aluno)
        if cin_rg:
            aluno_existente = Aluno.query.filter_by(cin_rg=cin_rg).first()
            if aluno_existente and aluno_existente.id != aluno_id:
                flash("RG já cadastrado para outro aluno.")
                return redirect(url_for("main.editar_aluno", aluno_id=aluno_id))
        
        # Verificar UID VT único (exceto o próprio aluno)
        if uid_vt:
            aluno_existente = Aluno.query.filter_by(uid_vt=uid_vt).first()
            if aluno_existente and aluno_existente.id != aluno_id:
                flash("UID VT já cadastrado para outro aluno.")
                return redirect(url_for("main.editar_aluno", aluno_id=aluno_id))
        
        # Converter data de nascimento
        data_nasc = None
        if data_nascimento:
            try:
                data_nasc = datetime.strptime(data_nascimento, '%Y-%m-%d').date()
            except ValueError:
                flash("Data de nascimento inválida.")
                return redirect(url_for("main.editar_aluno", aluno_id=aluno_id))
        
        # Atualizar dados do aluno
        aluno.nome = nome
        aluno.data_nascimento = data_nasc
        aluno.naturalidade = naturalidade
        aluno.cin_rg = cin_rg
        aluno.uid_vt = uid_vt
        aluno.email = email
        aluno.telefone = telefone
        aluno.cep = cep
        aluno.endereco = endereco
        aluno.bairro = bairro
        aluno.cidade = cidade
        aluno.estado = estado
        
        # Processar upload de nova foto
        foto = request.files.get('foto')
        if foto and foto.filename:
            foto_path = salvar_foto_aluno(foto, aluno.id)
            if foto_path:
                aluno.foto_path = foto_path
        
        # Dados do responsável (atualizar ou criar)
        nome_pai = request.form.get("nome_pai")
        nome_mae = request.form.get("nome_mae")
        telefone_responsavel = request.form.get("telefone_responsavel")
        email_responsavel = request.form.get("email_responsavel")
        endereco_responsavel = request.form.get("endereco_responsavel")
        
        responsavel = Responsavel.query.filter_by(aluno_id=aluno.id).first()
        
        if responsavel:
            responsavel.nome_pai = nome_pai
            responsavel.nome_mae = nome_mae
            responsavel.telefone = telefone_responsavel
            responsavel.email = email_responsavel
            responsavel.endereco = endereco_responsavel
        elif nome_pai or nome_mae or telefone_responsavel:
            responsavel = Responsavel(
                aluno_id=aluno.id,
                nome_pai=nome_pai,
                nome_mae=nome_mae,
                telefone=telefone_responsavel,
                email=email_responsavel,
                endereco=endereco_responsavel
            )
            db.session.add(responsavel)
        
        # Escola
        escola_id = request.form.get("escola_id")
        
        # Remove escolas anteriores e adiciona a nova
        AlunoEscola.query.filter_by(aluno_id=aluno.id).delete()
        
        if escola_id:
            aluno_escola = AlunoEscola(
                aluno_id=aluno.id,
                escola_id=int(escola_id)
            )
            db.session.add(aluno_escola)
        
        db.session.commit()
        
        flash("Aluno atualizado com sucesso!")
        return redirect(url_for("main.listar_alunos"))
    
    return render_template("admin_aluno_form.html",
                           aluno=aluno,
                           titulo="Editar Integrante",
                           escolas=escolas,
                           instrumentos=instrumentos,
                           tipos_instrumento=tipos_instrumento,
                           naipes=naipes)


@main_bp.route("/admin/aluno/toggle/<int:aluno_id>")
@login_required
@admin_required
def toggle_aluno(aluno_id):
    """Ativa ou inativa um aluno"""
    aluno = Aluno.query.get_or_404(aluno_id)
    
    aluno.ativo = not aluno.ativo
    db.session.commit()
    
    status = "ativado" if aluno.ativo else "inativado"
    flash(f"Aluno {status} com sucesso!")
    return redirect(url_for("main.listar_alunos"))


@main_bp.route("/admin/aluno/delete/<int:aluno_id>", methods=["POST"])
@login_required
@admin_required
def excluir_aluno(aluno_id):
    """Exclui um aluno (soft delete - inativa ao invés de excluir)"""
    aluno = Aluno.query.get_or_404(aluno_id)
    
    # Soft delete - apenas inativa
    aluno.ativo = False
    db.session.commit()
    
    flash("Aluno inativado com sucesso! (Dados preservados)")
    return redirect(url_for("main.listar_alunos"))


# ========================
# ROTAS PARA GESTÃO DE ESCOLAS
# ========================

@main_bp.route("/admin/escolas")
@login_required
@admin_required
def listar_escolas():
    """Lista todas as escolas"""
    escolas = Escola.query.order_by(Escola.nome).all()
    return render_template("admin_escolas.html", escolas=escolas)


@main_bp.route("/admin/escola/create", methods=["GET", "POST"])
@login_required
@admin_required
def criar_escola():
    """Cria uma nova escola"""
    if request.method == "POST":
        nome = request.form.get("nome")
        endereco = request.form.get("endereco")
        
        if not nome:
            flash("Nome da escola é obrigatório.")
            return redirect(url_for("main.criar_escola"))
        
        escola = Escola(nome=nome, endereco=endereco)
        db.session.add(escola)
        db.session.commit()
        
        flash("Escola criada com sucesso!")
        return redirect(url_for("main.listar_escolas"))
    
    return render_template("admin_escola_form.html", escola=None, titulo="Nova Escola")


@main_bp.route("/admin/escola/edit/<int:escola_id>", methods=["GET", "POST"])
@login_required
@admin_required
def editar_escola(escola_id):
    """Edita uma escola existente"""
    escola = Escola.query.get_or_404(escola_id)
    
    if request.method == "POST":
        nome = request.form.get("nome")
        endereco = request.form.get("endereco")
        
        if not nome:
            flash("Nome da escola é obrigatório.")
            return redirect(url_for("main.editar_escola", escola_id=escola_id))
        
        escola.nome = nome
        escola.endereco = endereco
        db.session.commit()
        
        flash("Escola atualizada com sucesso!")
        return redirect(url_for("main.listar_escolas"))
    
    return render_template("admin_escola_form.html", escola=escola, titulo="Editar Escola")


@main_bp.route("/admin/escola/delete/<int:escola_id>", methods=["POST"])
@login_required
@admin_required
def excluir_escola(escola_id):
    """Exclui uma escola"""
    escola = Escola.query.get_or_404(escola_id)
    
    db.session.delete(escola)
    db.session.commit()
    
    flash("Escola excluída com sucesso!")
    return redirect(url_for("main.listar_escolas"))


# ========================
# ROTAS PARA BUSCA DE CEP
# ========================

@main_bp.route("/admin/buscar-cep/<cep>")
@login_required
@admin_required
def buscar_cep(cep):
    """Busca CEP na tabela de logradouros local"""
    cep = cep.replace('-', '').replace('.', '')
    
    logradouro = Logradouro.query.filter_by(cep=cep).first()
    
    if logradouro:
        return jsonify({
            'success': True,
            'logradouro': {
                'cep': logradouro.cep,
                'tipo': logradouro.tipo,
                'descricao': logradouro.descricao,
                'bairro': logradouro.descricao_bairro,
                'cidade': logradouro.descricao_cidade,
                'uf': logradouro.uf,
                'complemento': logradouro.complemento
            }
        })
    
    return jsonify({'success': False, 'message': 'CEP não encontrado'})


@main_bp.route("/admin/salvar-logradouro", methods=["POST"])
@login_required
@admin_required
def salvar_logradouro():
    """Salva novo logradouro buscado da API ViaCEP"""
    data = request.get_json()
    
    cep = data.get('cep', '').replace('-', '').replace('.', '')
    
    # Verificar se já existe
    existente = Logradouro.query.filter_by(cep=cep).first()
    if existente:
        return jsonify({'success': True, 'message': 'CEP já existe'})
    
    # Buscar ou criar cidade
    cidade_nome = data.get('descricao_cidade', '')
    uf = data.get('uf', 'SP')
    
    cidade = Cidade.query.filter(
        Cidade.descricao.ilike(f'%{cidade_nome}%'),
        Cidade.uf == uf
    ).first()
    
    if not cidade:
        # Criar cidade se não existir
        cidade = Cidade(
            descricao=cidade_nome,
            uf=uf,
            codigo_ibge=None,
            ddd=None
        )
        db.session.add(cidade)
        db.session.flush()
    
    # Criar logradouro
    logradouro = Logradouro(
        cep=cep,
        tipo=data.get('tipo', ''),
        descricao=data.get('descricao', ''),
        cidade_id=cidade.id,
        uf=uf,
        complemento=data.get('complemento'),
        descricao_sem_numero=data.get('descricao', ''),
        descricao_cidade=cidade_nome,
        codigo_cidade_ibge=cidade.codigo_ibge,
        descricao_bairro=data.get('descricao_bairro', '')
    )
    
    db.session.add(logradouro)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Logradouro salvo com sucesso'})


# ========================
# UPLOAD DE FOTOS
# ========================


def salvar_foto_aluno(foto_file, aluno_id):
    """Salva a foto do aluno e retorna o caminho"""
    if not foto_file or foto_file.filename == '':
        return None
    
    # Extensões permitidas
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    if allowed_file(foto_file.filename):
        # Criar nome do arquivo com ID único
        ext = foto_file.filename.rsplit('.', 1)[1].lower()
        filename = f"aluno_{aluno_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
        
        # Caminho para salvar
        upload_folder = os.path.join('static', 'uploads', 'alunos')
        
        # Criar diretório se não existir
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        foto_file.save(filepath)
        
        # Retornar caminho relativo para salvar no banco
        return os.path.join('uploads', 'alunos', filename)
    
    return None


# ========================
# ROTAS PARA RELATÓRIOS DE ALUNOS
# ========================

@main_bp.route("/admin/relatorios-alunos")
@login_required
@admin_required
def relatorios_alunos():
    """Página inicial dos relatórios de alunos"""
    return render_template("relatorios_alunos.html")


@main_bp.route("/admin/relatorio-geral-alunos")
@login_required
@admin_required
def relatorio_geral_alunos():
    """Relatório geral de alunos ativos"""
    from datetime import datetime
    
    # Query para alunos ativos com JOIN responsável e escola
    alunos = Aluno.query.outerjoin(Responsavel).outerjoin(AlunoEscola).outerjoin(Escola).filter(
        Aluno.ativo == True
    ).order_by(Aluno.nome).all()
    
    total_alunos = Aluno.query.filter(Aluno.ativo == True).count()
    data_geracao = datetime.now()
    
    return render_template("relatorio_geral_alunos.html", 
                           alunos=alunos, 
                           total_alunos=total_alunos,
                           data_geracao=data_geracao)


@main_bp.route("/admin/relatorio-aluno/<int:aluno_id>")
@login_required
@admin_required
def relatorio_aluno(aluno_id):
    """Relatório individual do aluno (resguardando dados sensíveis)"""
    aluno = Aluno.query.options(
        db.joinedload(Aluno.responsaveis),
        db.joinedload(Aluno.escolas).joinedload(AlunoEscola.escola)
    ).get_or_404(aluno_id)
    
    if not aluno.ativo:
        flash("Relatório só disponível para alunos ativos")
        return redirect(url_for('main.listar_alunos'))
    
    data_geracao = datetime.now()
    
    return render_template("relatorio_aluno_individual.html", 
                           aluno=aluno, 
                           data_geracao=data_geracao)
