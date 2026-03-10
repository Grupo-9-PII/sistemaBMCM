CREATE TABLE alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    data_nascimento DATE,
    naturalidade TEXT,
    cin_rg TEXT UNIQUE,
    email TEXT,
    telefone TEXT,
    endereco TEXT,
    cidade TEXT,
    foto_path TEXT,
    ativo BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE responsaveis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER,
    nome_pai TEXT,
    nome_mae TEXT,
    telefone TEXT,

    FOREIGN KEY (aluno_id) REFERENCES alunos(id)
);


CREATE TABLE escolas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    endereco TEXT
);


CREATE TABLE aluno_escola (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER,
    escola_id INTEGER,

    FOREIGN KEY (aluno_id) REFERENCES alunos(id),
    FOREIGN KEY (escola_id) REFERENCES escolas(id)
);


CREATE TABLE funcoes_banda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_funcao TEXT
);


CREATE TABLE instrumentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT
);


CREATE TABLE aluno_instrumento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER,
    instrumento_id INTEGER,

    FOREIGN KEY (aluno_id) REFERENCES alunos(id),
    FOREIGN KEY (instrumento_id) REFERENCES instrumentos(id)
);


CREATE TABLE uniformes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER,
    data_entrega DATE,

    FOREIGN KEY (aluno_id) REFERENCES alunos(id)
);


CREATE TABLE presencas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER,
    data_presenca DATE,
    presente BOOLEAN,

    FOREIGN KEY (aluno_id) REFERENCES alunos(id)
);


CREATE TABLE naipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT
);


CREATE TABLE tipos_instrumento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT
);

INSERT INTO tipos_instrumento (nome) VALUES ('Sopro');
INSERT INTO tipos_instrumento (nome) VALUES ('Percussão');
INSERT INTO tipos_instrumento (nome) VALUES ('Metais');

CREATE TABLE instrumentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    nome TEXT NOT NULL,

    tipo_id INTEGER,

    patrimonio TEXT UNIQUE,

    marca TEXT,
    modelo TEXT,

    estado TEXT,

    data_aquisicao DATE,

    observacoes TEXT,

    ativo BOOLEAN DEFAULT 1,

    FOREIGN KEY (tipo_id) REFERENCES tipos_instrumento(id)
);

