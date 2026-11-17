import os

from flask import Flask

from .models import db


def create_app(config=None):
    app = Flask(__name__)
    producao = os.environ.get("FLASK_ENV") == "production"
    chave = os.environ.get("SECRET_KEY")
    if producao and not chave:
        raise RuntimeError("Defina SECRET_KEY nas variáveis de ambiente.")
    url = os.environ.get("DATABASE_URL", "sqlite:///cesta_certa.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    app.config.update(
        SECRET_KEY=chave or "somente-desenvolvimento",
        SQLALCHEMY_DATABASE_URI=url,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=producao,
        PERMANENT_SESSION_LIFETIME=1800,
    )
    if config:
        app.config.update(config)
    db.init_app(app)

    from .cli import register_cli
    from .routes import bp, register_security
    app.register_blueprint(bp)
    register_security(app)
    register_cli(app)
    with app.app_context():
        db.create_all()
    return app
