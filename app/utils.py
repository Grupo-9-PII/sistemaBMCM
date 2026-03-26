
from functools import wraps
import os
from flask import redirect, url_for, flash
from flask_login import current_user
from .models import User, TipoInstrumento, Naipe, FuncaoBanda, Cidade, Logradouro
from . import db
from sqlalchemy import text

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


def importar_municipios():
    """Importa dados de municípios e logradouros do arquivo SQL"""
    
    # Verificar se já existem dados
    if Cidade.query.first():
        return  # Dados já foram importados
    
    # Caminho para o arquivo SQL
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sql_file = os.path.join(base_dir, "municipios.sql")
    
    if not os.path.exists(sql_file):
        return
    
    # Ler e executar o arquivo SQL
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Executar SQL diretamente no banco de dados
    import re
    
    # Buscar INSERTs da tabela cidade
    cidade_pattern = r"INSERT INTO `cidade` VALUES ([^;]+);"
    cidade_matches = re.findall(cidade_pattern, sql_content, re.DOTALL)
    
    for match in cidade_matches:
        # Parse dos valores
        values = match.strip()
        if values.startswith('(') and values.endswith(')'):
            # Parse dos campos: (id,'nome',uf,codigo_ibge,ddd)
            values = values[1:-1]  # Remove parênteses externos
            parts = values.split('),(')
            
            for part in parts:
                part = part.strip().strip('()')
                if part:
                    # Separar os campos
                    campos = part.split(',')
                    if len(campos) >= 5:
                        # Remover aspas e espaços
                        id_val = int(campos[0].strip())
                        nome = campos[1].strip().strip("'")
                        uf = campos[2].strip().strip("'")
                        cod_ibge = int(campos[3].strip())
                        ddd = campos[4].strip().strip("'")
                        
                        cidade = Cidade(
                            id=id_val,
                            descricao=nome,
                            uf=uf,
                            codigo_ibge=cod_ibge,
                            ddd=ddd
                        )
                        db.session.add(cidade)
    
    db.session.commit()
    
    # Executar INSERTs da tabela logradouro
    logradouro_pattern = r"INSERT INTO `logradouro` VALUES ([^;]+);"
    logradouro_matches = re.findall(logradouro_pattern, sql_content, re.DOTALL)
    
    for match in logradouro_matches:
        values = match.strip()
        if values.startswith('(') and values.endswith(')'):
            values = values[1:-1]
            parts = values.split('),(')
            
            for part in parts:
                part = part.strip().strip('()')
                if part:
                    campos = part.split(',')
                    if len(campos) >= 11:
                        cep = campos[0].strip().strip("'")
                        id_val = int(campos[1].strip())
                        tipo = campos[2].strip().strip("'")
                        descricao = campos[3].strip().strip("'")
                        cidade_id = int(campos[4].strip())
                        uf = campos[5].strip().strip("'")
                        complemento = campos[6].strip().strip("'") if campos[6].strip() != 'NULL' else None
                        descricao_sem_numero = campos[7].strip().strip("'") if campos[7].strip() != 'NULL' else None
                        descricao_cidade = campos[8].strip().strip("'") if campos[8].strip() != 'NULL' else None
                        codigo_cidade_ibge = int(campos[9].strip()) if campos[9].strip() != 'NULL' else None
                        descricao_bairro = campos[10].strip().strip("'") if campos[10].strip() != 'NULL' else None
                        
                        logradouro = Logradouro(
                            cep=cep,
                            id=id_val,
                            tipo=tipo,
                            descricao=descricao,
                            cidade_id=cidade_id,
                            uf=uf,
                            complemento=complemento,
                            descricao_sem_numero=descricao_sem_numero,
                            descricao_cidade=descricao_cidade,
                            codigo_cidade_ibge=codigo_cidade_ibge,
                            descricao_bairro=descricao_bairro
                        )
                        db.session.add(logradouro)
    
    db.session.commit()


def migrar_banco_novos_campos():
    """Adiciona os novos campos ao banco de dados se não existirem"""
    try:
        # Verificar se a coluna cep existe na tabela aluno
        result = db.session.execute(text("PRAGMA table_info(aluno)"))
        columns = [row[1] for row in result.fetchall()]
        
        # Adicionar coluna cep se não existir
        if 'cep' not in columns:
            db.session.execute(text("ALTER TABLE aluno ADD COLUMN cep VARCHAR(10)"))
        
        # Adicionar coluna bairro se não existir
        if 'bairro' not in columns:
            db.session.execute(text("ALTER TABLE aluno ADD COLUMN bairro VARCHAR(100)"))
        
        # Adicionar coluna estado se não existir
        if 'estado' not in columns:
            db.session.execute(text("ALTER TABLE aluno ADD COLUMN estado VARCHAR(2)"))
        
        db.session.commit()
    except Exception as e:
        print(f"Erro na migração: {e}")
        db.session.rollback()

