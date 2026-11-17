import pytest

from app.models import Item
from app.services import (RegraError, buscar_familias, cadastrar_familia, painel_estoque,
                          registrar_movimentacao, saldo)


def test_cadastra_familia_valida(app):
    f = cadastrar_familia("Família Teste (demonstração)", "(11) 90000-0000", 4)
    assert f.id and f.numero_pessoas == 4


def test_recusa_duplicidade_ignorando_maiusculas(app):
    cadastrar_familia("Souza", "111", 3)
    with pytest.raises(RegraError, match="já existe"):
        cadastrar_familia("souza", "111", 3)


@pytest.mark.parametrize("nome,contato,pessoas", [("", "1", 2), ("A", "", 2), ("A", "1", 0), ("A", "1", "x")])
def test_recusa_dados_invalidos(app, nome, contato, pessoas):
    with pytest.raises(RegraError):
        cadastrar_familia(nome, contato, pessoas)


def test_busca_trata_texto_como_dado(app):
    cadastrar_familia("Souza", "1", 2)
    assert len(buscar_familias("sou")) == 1
    assert buscar_familias("' OR '1'='1") == []


def test_saldo_entradas_menos_saidas(app):
    item = Item.query.first()
    f = cadastrar_familia("Lima", "2", 3)
    registrar_movimentacao(item.id, "entrada", 10)
    registrar_movimentacao(item.id, "saida", 4, f.id)
    assert saldo(item.id) == 6


def test_saida_nao_deixa_saldo_negativo(app):
    item = Item.query.first()
    f = cadastrar_familia("Lima", "2", 3)
    registrar_movimentacao(item.id, "entrada", 2)
    with pytest.raises(RegraError, match="Saldo insuficiente"):
        registrar_movimentacao(item.id, "saida", 5, f.id)


def test_quantidade_deve_ser_positiva(app):
    with pytest.raises(RegraError):
        registrar_movimentacao(Item.query.first().id, "entrada", 0)


def test_alerta_de_estoque_baixo(app):
    item = Item.query.first()
    registrar_movimentacao(item.id, "entrada", 3)
    assert painel_estoque()[0]["baixo"] is True
    registrar_movimentacao(item.id, "entrada", 20)
    assert painel_estoque()[0]["baixo"] is False
