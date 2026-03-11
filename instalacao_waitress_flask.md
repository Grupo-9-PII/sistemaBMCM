# Implantação do Sistema Web (Flask + Waitress)

Guia de instalação e execução do sistema da **Banda Marcial de Marília** utilizando **Python, Flask, SQLite e Waitress** em ambiente Windows.

---

# 1. Visão Geral da Arquitetura

O sistema utiliza a seguinte estrutura:

```
Navegador
   ↓
Waitress (Servidor WSGI)
   ↓
Flask (Aplicação Web)
   ↓
SQLite (Banco de Dados)
```

O **Waitress** é um servidor WSGI utilizado para executar aplicações Python em ambiente de produção no Windows.

---

# 2. Pré-requisitos

Antes da instalação, verifique se o sistema possui:

* Windows 10 ou superior
* Python 3.10+ instalado
* Acesso ao terminal (Prompt ou PowerShell)

---

# 3. Instalação do Python

Baixar o Python no site oficial:

https://www.python.org/downloads/

Durante a instalação marcar a opção:

```
Add Python to PATH
```

Verificar instalação:

```bash
python --version
```

---

# 4. Estrutura do Sistema

Criar uma pasta para o sistema:

```
C:\sistema_banda
```

Estrutura recomendada:

```
sistema_banda
│
├── app.py
├── run.py
├── database.db
├── requirements.txt
│
├── templates
│
├── static
│
└── venv
```

---

# 5. Criar Ambiente Virtual

Entrar na pasta do sistema:

```bash
cd C:\sistema_banda
```

Criar ambiente virtual:

```bash
python -m venv venv
```

Ativar ambiente virtual:

```bash
venv\Scripts\activate
```

---

# 6. Instalar Dependências

Instalar Flask e Waitress:

```bash
pip install flask
pip install waitress
```

Gerar arquivo de dependências:

```bash
pip freeze > requirements.txt
```

---

# 7. Aplicação Flask (app.py)

Exemplo simples de aplicação:

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Sistema Banda Marcial de Marília"

```

---

# 8. Arquivo de Inicialização do Servidor

Criar o arquivo:

```
run.py
```

Conteúdo:

```python
from waitress import serve
from app import app

serve(app, host="0.0.0.0", port=5000)
```

Esse arquivo inicia o servidor Waitress.

---

# 9. Executar o Sistema

Com o ambiente virtual ativo:

```bash
python run.py
```

Acessar no navegador:

```
http://localhost:5000
```

Se estiver na rede local:

```
http://IP_DO_SERVIDOR:5000
```

---

# 10. Acesso pela Rede

Para descobrir o IP da máquina:

```bash
ipconfig
```

Exemplo de acesso:

```
http://192.168.0.10:5000
```

---

# 11. Execução Automática (Opcional)

O sistema pode ser iniciado automaticamente criando um **script .bat**.

Arquivo:

```
iniciar_sistema.bat
```

Conteúdo:

```
cd C:\sistema_banda
venv\Scripts\activate
python run.py
```

---

# 12. Banco de Dados

O sistema utiliza:

```
SQLite
```

Arquivo do banco:

```
database.db
```

Vantagens:

* não necessita servidor
* fácil backup
* simples manutenção

---

# 13. Backup do Sistema

Para backup basta copiar:

```
database.db
```

Recomendado realizar backup periódico.

---

# 14. Considerações Futuras

Possíveis evoluções do sistema:

* autenticação de usuários
* controle de presença
* cadastro de instrumentos
* relatórios administrativos
* integração com RFID para controle de acesso

---

# 15. Observações

O Waitress foi escolhido porque:

* funciona muito bem no Windows
* não necessita Apache ou Nginx
* é simples de configurar
* é estável para aplicações internas

Para ambientes maiores no futuro poderá ser utilizado:

```
Linux + Nginx + Gunicorn
```

---

**Sistema desenvolvido para gerenciamento da Banda Marcial de Marília.**

Projeto acadêmico – UNIVESP.
