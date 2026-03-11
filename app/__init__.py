
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Por favor, faça login para acessar esta página."

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(Config.BASE_DIR, "templates"),
        static_folder=os.path.join(Config.BASE_DIR, "static"),
    )
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from .auth import auth_bp
    from .routes import main_bp
    from .utils import criar_admin_padrao, criar_dados_iniciais

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        instance_dir = os.path.join(Config.BASE_DIR, "instance")
        if not os.path.exists(instance_dir):
            os.makedirs(instance_dir, exist_ok=True)
        
        # Criar todas as tabelas no banco de dados
        db.create_all()
        
        # Criar admin padrão
        criar_admin_padrao()
        
        # Criar dados iniciais (tipos de instrumento, naipes, funções)
        criar_dados_iniciais()

    return app

