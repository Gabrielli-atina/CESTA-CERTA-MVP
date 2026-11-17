"""Regras de negócio do MVP (RF01, RF02, RF03), separadas da interface."""
from sqlalchemy import func

from .models import Familia, Item, Movimentacao, db


class RegraError(ValueError):
    """Erro de regra de negócio, com mensagem segura para o usuário."""


def cadastrar_familia(nome, contato, pessoas):
    nome, contato = (nome or "").strip(), (contato or "").strip()
    if not nome:
        raise RegraError("Informe o nome do responsável.")
    if not contato:
        raise RegraError("Informe o contato.")
    if len(nome) > 120 or len(contato) > 30:
        raise RegraError("Nome ou contato acima do tamanho permitido.")
    try:
        pessoas = int(pessoas)
    except (TypeError, ValueError):
        pessoas = 0
    if pessoas <= 0:
        raise RegraError("Informe o número de pessoas (maior que zero).")
    existe = Familia.query.filter(
        func.lower(Familia.nome_responsavel) == nome.lower(),
        Familia.contato == contato,
    ).first()
    if existe:
        raise RegraError("Esta família já existe. Busque pelo nome no Início.")
    familia = Familia(nome_responsavel=nome, contato=contato, numero_pessoas=pessoas)
    db.session.add(familia)
    db.session.commit()
    return familia


def buscar_familias(termo):
    termo = (termo or "").strip().lower()
    if not termo:
        return []
    return Familia.query.filter(
        func.lower(Familia.nome_responsavel).contains(termo, autoescape=True)
    ).all()


def saldo(item_id):
    total = db.session.query(
        func.coalesce(
            func.sum(
                db.case((Movimentacao.tipo == "entrada", Movimentacao.quantidade),
                        else_=-Movimentacao.quantidade)
            ),
            0,
        )
    ).filter(Movimentacao.item_id == item_id).scalar()
    return float(total)


def registrar_movimentacao(item_id, tipo, quantidade, familia_id=None):
    item = db.session.get(Item, item_id)
    if item is None:
        raise RegraError("Item não encontrado.")
    if tipo not in ("entrada", "saida"):
        raise RegraError("Tipo de movimentação inválido.")
    try:
        quantidade = float(quantidade)
    except (TypeError, ValueError):
        quantidade = 0
    if quantidade <= 0:
        raise RegraError("Informe uma quantidade maior que zero.")
    if tipo == "saida":
        if not familia_id or db.session.get(Familia, familia_id) is None:
            raise RegraError("Escolha a família atendida.")
        atual = saldo(item.id)
        if quantidade > atual:
            raise RegraError(f"Saldo insuficiente: há só {atual:g} {item.unidade} de {item.nome}.")
    mov = Movimentacao(item_id=item.id, tipo=tipo, quantidade=quantidade,
                       familia_id=familia_id if tipo == "saida" else None)
    db.session.add(mov)
    db.session.commit()
    return mov


def painel_estoque():
    """Lista itens com saldo e indicação de estoque baixo (RF03)."""
    linhas = []
    for item in Item.query.order_by(Item.nome).all():
        s = saldo(item.id)
        linhas.append({"item": item, "saldo": s, "baixo": s < item.estoque_minimo})
    return linhas
