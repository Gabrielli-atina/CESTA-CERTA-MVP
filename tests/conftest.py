import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import Item, Usuario, db
from app.routes import TENTATIVAS


@pytest.fixture()
def app():
    TENTATIVAS.clear()
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
    with app.app_context():
        db.session.add(Usuario(username="demo",
                               senha_hash=generate_password_hash("senha-de-teste", method="scrypt")))
        db.session.add(Item(nome="Arroz", unidade="kg", estoque_minimo=10))
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def token(client, url="/login"):
    client.get(url)
    with client.session_transaction() as s:
        return s["_csrf"]


@pytest.fixture()
def logado(client):
    t = token(client)
    client.post("/login", data={"username": "demo", "password": "senha-de-teste", "_csrf": t})
    return client
