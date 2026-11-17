import click
from werkzeug.security import generate_password_hash

from .models import Item, Usuario, db


def register_cli(app):
    @app.cli.command("create-user")
    @click.argument("username")
    @click.password_option()
    def create_user(username, password):
        """Cria o usuário da coordenadora (senha lida sem eco, nunca no código)."""
        if len(password) < 8:
            raise click.ClickException("A senha deve ter pelo menos 8 caracteres.")
        db.session.add(Usuario(username=username,
                               senha_hash=generate_password_hash(password, method="scrypt")))
        db.session.commit()
        click.echo("Usuário criado.")

    @app.cli.command("seed")
    def seed():
        """Cadastra itens de demonstração (dados fictícios)."""
        for nome, un, minimo in [("Arroz", "kg", 10), ("Óleo", "litros", 10),
                                 ("Feijão", "kg", 10), ("Macarrão", "kg", 8)]:
            if not Item.query.filter_by(nome=nome).first():
                db.session.add(Item(nome=nome, unidade=un, estoque_minimo=minimo))
        db.session.commit()
        click.echo("Itens de demonstração criados.")
