
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


# ========================
# MODELO DE USUÁRIO (Auth)
# ========================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    must_change_password = db.Column(db.Boolean, default=True)

    login_attempts = db.Column(db.Integer, default=0)
    blocked_until = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# ========================
# MODELOS DE BANDA MARCIAL
# ========================

# Tabela de referência: Naipe (seções da banda)
class Naipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    
    # Relacionamento com instrumentos
    instrumentos = db.relationship('Instrumento', backref='naipe', lazy=True)


# Tabela de referência: Funções na banda
class FuncaoBanda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_funcao = db.Column(db.String(100), nullable=False)


# Tabela de referência: Tipos de instrumento
class TipoInstrumento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    
    # Relacionamento com instrumentos
    instrumentos = db.relationship('Instrumento', backref='tipo', lazy=True)


# Tabela: Escolas
class Escola(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    endereco = db.Column(db.String(300))
    
    # Relacionamento com alunos
    alunos = db.relationship('AlunoEscola', backref='escola', lazy=True)


# Tabela: Alunos
class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=True)
    naturalidade = db.Column(db.String(100))
    cin_rg = db.Column(db.String(20), unique=True)
    uid_vt = db.Column(db.String(20), unique=True, nullable=True)
    email = db.Column(db.String(150))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(300))
    cidade = db.Column(db.String(100))
    foto_path = db.Column(db.String(500))
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    responsaveis = db.relationship('Responsavel', backref='aluno', lazy=True, cascade='all, delete-orphan')
    uniforme = db.relationship('Uniforme', backref='aluno', lazy=True, cascade='all, delete-orphan')
    presencas = db.relationship('Presenca', backref='aluno', lazy=True, cascade='all, delete-orphan')
    instrumentos = db.relationship('AlunoInstrumento', backref='aluno', lazy=True, cascade='all, delete-orphan')
    escolas = db.relationship('AlunoEscola', backref='aluno', lazy=True, cascade='all, delete-orphan')


# Tabela: Responsáveis (pais/responsáveis)
class Responsavel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    nome_pai = db.Column(db.String(200))
    nome_mae = db.Column(db.String(200))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(150))
    endereco = db.Column(db.String(300))


# Tabela: Relação Aluno-Escola
class AlunoEscola(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    escola_id = db.Column(db.Integer, db.ForeignKey('escola.id'), nullable=False)
    data_matricula = db.Column(db.Date, default=datetime.utcnow().date)


# Tabela: Instrumentos
class Instrumento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipo_instrumento.id'))
    naipe_id = db.Column(db.Integer, db.ForeignKey('naipe.id'))
    patrimonio = db.Column(db.String(50), unique=True)
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    estado = db.Column(db.String(50))  # Novo, Bom, Regular, Ruim
    data_aquisicao = db.Column(db.Date)
    observacoes = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamento com alunos
    alunos = db.relationship('AlunoInstrumento', backref='instrumento', lazy=True, cascade='all, delete-orphan')


# Tabela: Relação Aluno-Instrumento
class AlunoInstrumento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    instrumento_id = db.Column(db.Integer, db.ForeignKey('instrumento.id'), nullable=False)
    data_emprestimo = db.Column(db.Date, default=datetime.utcnow().date)
    data_devolucao = db.Column(db.Date, nullable=True)
    observacoes = db.Column(db.Text)


# Tabela: Uniformes
class Uniforme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    data_entrega = db.Column(db.Date)
    tamanho = db.Column(db.String(10))
    observacoes = db.Column(db.Text)


# Tabela: Presenças
class Presenca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    data_presenca = db.Column(db.Date, default=datetime.utcnow().date)
    presente = db.Column(db.Boolean, default=True)
    observacoes = db.Column(db.Text)

