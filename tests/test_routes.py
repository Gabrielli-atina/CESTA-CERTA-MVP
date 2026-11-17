from tests.conftest import token


def test_rota_protegida_redireciona_sem_login(client):
    r = client.get("/")
    assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_login_valido_e_invalido(client):
    t = token(client)
    r = client.post("/login", data={"username": "demo", "password": "errada", "_csrf": t})
    assert "Usuário ou senha inválidos" in r.get_data(as_text=True)
    r = client.post("/login", data={"username": "demo", "password": "senha-de-teste", "_csrf": t})
    assert r.status_code == 302


def test_post_sem_csrf_e_recusado(client):
    assert client.post("/login", data={"username": "demo", "password": "x"}).status_code == 400


def test_bloqueio_apos_5_erros(client):
    t = token(client)
    for _ in range(5):
        client.post("/login", data={"username": "demo", "password": "errada", "_csrf": t})
    r = client.post("/login", data={"username": "demo", "password": "senha-de-teste", "_csrf": t})
    assert "Muitas tentativas" in r.get_data(as_text=True)


def test_script_digitado_aparece_como_texto(logado):
    t = token(logado, "/familias/nova")
    logado.post("/familias/nova", data={"nome": "<script>alert(1)</script>", "contato": "1",
                                        "pessoas": "2", "_csrf": t})
    html = logado.get("/?q=script").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html and "&lt;script&gt;" in html


def test_logout_encerra_sessao(logado):
    t = token(logado, "/")
    logado.post("/logout", data={"_csrf": t})
    assert logado.get("/").status_code == 302
