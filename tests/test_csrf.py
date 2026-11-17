from flask import session

from app import create_app
from app.routes import csrf_valido


def test_csrf_valido_exige_token_correto_na_sessao():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
    with app.test_request_context():
        assert csrf_valido("") is False
        session["_csrf"] = "abc"
        assert csrf_valido("x") is False
        assert csrf_valido("abc") is True
