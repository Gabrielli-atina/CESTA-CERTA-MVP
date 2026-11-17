import hmac
import secrets
import time
from functools import wraps

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash

from . import services
from .models import Familia, Item, Usuario

bp = Blueprint("main", __name__)
TENTATIVAS = {}  # username -> (erros, bloqueado_ate)
MAX_ERROS, BLOQUEIO_S = 5, 15 * 60


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "uid" not in session:
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapped


def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(16)
    return session["_csrf"]
def csrf_valido(enviado):
    esperado = session.get("_csrf")
    return bool(esperado) and hmac.compare_digest(enviado, esperado)


def register_security(app):
    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def checar_csrf():
        if request.method == "POST" and not csrf_valido(request.form.get("_csrf", "")):
            abort(400)

    @app.after_request
    def cabecalhos(resp):
        resp.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        resp.headers["X-Content-Type-Options"] = "nosniff"
        return resp

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(500)
    def erro(_e):
        return render_template("erro.html"), getattr(_e, "code", 500)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        erros, ate = TENTATIVAS.get(username, (0, 0))
        if ate > time.time():
            flash("Muitas tentativas. Aguarde 15 minutos e tente de novo.", "erro")
        else:
            user = Usuario.query.filter_by(username=username).first()
            if user and check_password_hash(user.senha_hash, request.form.get("password", "")):
                TENTATIVAS.pop(username, None)
                session.clear()
                session["uid"] = user.id
                session.permanent = True
                return redirect(url_for("main.home"))
            erros += 1
            TENTATIVAS[username] = (erros, time.time() + BLOQUEIO_S if erros >= MAX_ERROS else 0)
            flash("Usuário ou senha inválidos.", "erro")
    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@bp.route("/")
@login_required
def home():
    q = request.args.get("q", "")
    return render_template("home.html", q=q, resultados=services.buscar_familias(q))


@bp.route("/familias/nova", methods=["GET", "POST"])
@login_required
def nova_familia():
    if request.method == "POST":
        try:
            services.cadastrar_familia(request.form.get("nome"), request.form.get("contato"),
                                       request.form.get("pessoas"))
            flash("Família cadastrada.", "ok")
            return redirect(url_for("main.nova_familia"))
        except services.RegraError as e:
            flash(str(e), "erro")
    return render_template("familia.html")


@bp.route("/estoque")
@login_required
def estoque():
    return render_template("estoque.html", linhas=services.painel_estoque())


@bp.route("/estoque/movimentar", methods=["GET", "POST"])
@login_required
def movimentar():
    if request.method == "POST":
        try:
            services.registrar_movimentacao(
                request.form.get("item_id", type=int), request.form.get("tipo"),
                request.form.get("quantidade"), request.form.get("familia_id", type=int))
            return redirect(url_for("main.estoque"))
        except services.RegraError as e:
            flash(str(e), "erro")
    return render_template("movimentar.html", itens=Item.query.order_by(Item.nome).all(),
                           familias=Familia.query.order_by(Familia.nome_responsavel).all())
