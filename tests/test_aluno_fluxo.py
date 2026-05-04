import os

import pytest


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    # Evita carga pesada de municípios durante os testes.
    import app.utils as utils
    monkeypatch.setattr(utils, "importar_municipios", lambda: None)

    from app import create_app, db
    from app.models import User

    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        user = User.query.filter_by(username="tester").first()
        if not user:
            user = User(
                username="tester",
                is_admin=True,
                must_change_password=False,
            )
            user.set_password("123456")
            db.session.add(user)
            db.session.commit()

    with app.test_client() as client:
        resp = client.post(
            "/login",
            data={"username": "tester", "password": "123456"},
            follow_redirects=False,
        )
        assert resp.status_code in (302, 303)
        yield client


def test_criar_aluno_persiste_registro(client):
    from app.models import Aluno

    response = client.post(
        "/admin/aluno/create",
        data={
            "nome": "Aluno Teste",
            "cin_rg": "12.345.678-9",
            "email": "aluno.teste@example.com",
            "telefone": "(11) 91234-5678",
            "data_nascimento": "",
            "naturalidade": "Sao Paulo",
            "cep": "01001-000",
            "endereco": "Rua Teste",
            "numero": "123",
            "complemento": "",
            "bairro": "Centro",
            "cidade": "Sao Paulo",
            "estado": "SP",
            "data_entrada_banda": "2023-01-15",
            "data_desligamento_banda": "",
        },
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert "/admin/alunos" in response.headers.get("Location", "")

    aluno = Aluno.query.filter_by(cin_rg="12.345.678-9").first()
    assert aluno is not None
    assert aluno.nome == "ALUNO TESTE"
    assert aluno.email == "aluno.teste@example.com"
    assert aluno.ativo == True  # Deve ser ativo quando não há data de desligamento


def test_criar_aluno_desligado_inativa_registro(client):
    from app.models import Aluno

    response = client.post(
        "/admin/aluno/create",
        data={
            "nome": "Aluno Desligado",
            "cin_rg": "98.765.432-1",
            "email": "desligado@example.com",
            "telefone": "(11) 99876-5432",
            "data_nascimento": "",
            "naturalidade": "Campinas",
            "cep": "13010-111",
            "endereco": "Rua Desligada",
            "numero": "456",
            "complemento": "",
            "bairro": "Centro",
            "cidade": "Campinas",
            "estado": "SP",
            "data_entrada_banda": "2022-03-10",
            "data_desligamento_banda": "2024-12-31",
        },
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert "/admin/alunos" in response.headers.get("Location", "")

    aluno = Aluno.query.filter_by(cin_rg="98.765.432-1").first()
    assert aluno is not None
    assert aluno.nome == "ALUNO DESLIGADO"
    assert aluno.email == "desligado@example.com"
    assert aluno.ativo == False  # Deve ser inativo quando há data de desligamento


def test_editar_aluno_atualiza_registro(client):
    from app import db
    from app.models import Aluno

    aluno = Aluno(nome="ALUNO ORIGINAL", cin_rg="11.111.111-1")
    db.session.add(aluno)
    db.session.commit()

    response = client.post(
        f"/admin/aluno/edit/{aluno.id}",
        data={
            "nome": "Aluno Alterado",
            "cin_rg": "22.222.222-2",
            "email": "alterado@example.com",
            "telefone": "(11) 93456-7890",
            "data_nascimento": "",
            "naturalidade": "Campinas",
            "cep": "13010-111",
            "endereco": "Avenida Alterada",
            "numero": "456",
            "complemento": "Sala 1",
            "bairro": "Centro",
            "cidade": "Campinas",
            "estado": "SP",
            "data_entrada_banda": "2023-02-20",
            "data_desligamento_banda": "2024-12-31",
        },
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert "/admin/alunos" in response.headers.get("Location", "")

    aluno_atualizado = Aluno.query.get(aluno.id)
    assert aluno_atualizado is not None
    assert aluno_atualizado.nome == "ALUNO ALTERADO"
    assert aluno_atualizado.cin_rg == "22.222.222-2"
    assert aluno_atualizado.email == "alterado@example.com"
    assert aluno_atualizado.ativo == False  # Deve ser inativo quando data de desligamento é definida


def test_criar_aluno_com_documento_tipo_cpf(client):
    from app.models import Aluno

    response = client.post(
        "/admin/aluno/create",
        data={
            "nome": "Aluno CPF",
            "cin_rg": "123.456.789-01",
            "email": "cpf@example.com",
            "telefone": "(11) 99876-5432",
            "data_nascimento": "",
            "naturalidade": "Guarulhos",
            "cep": "07010-000",
            "endereco": "Rua Documento",
            "numero": "10",
            "complemento": "",
            "bairro": "Centro",
            "cidade": "Guarulhos",
            "estado": "SP",
        },
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert "/admin/alunos" in response.headers.get("Location", "")

    aluno = Aluno.query.filter_by(email="cpf@example.com").first()
    assert aluno is not None
    assert aluno.cin_rg == "123.456.789-01"
