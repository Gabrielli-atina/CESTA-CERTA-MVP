from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def agora():
    return datetime.now(timezone.utc)


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    senha_hash = db.Column(db.String(300), nullable=False)


class Familia(db.Model):
    __table_args__ = (db.UniqueConstraint("nome_responsavel", "contato"),)
    id = db.Column(db.Integer, primary_key=True)
    nome_responsavel = db.Column(db.String(120), nullable=False)
    contato = db.Column(db.String(30), nullable=False)
    numero_pessoas = db.Column(db.Integer, nullable=False)
    data_cadastro = db.Column(db.DateTime, default=agora)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    unidade = db.Column(db.String(20), nullable=False)
    estoque_minimo = db.Column(db.Float, nullable=False, default=0)


class Movimentacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # entrada | saida
    quantidade = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=agora)
    familia_id = db.Column(db.Integer, db.ForeignKey("familia.id"))
