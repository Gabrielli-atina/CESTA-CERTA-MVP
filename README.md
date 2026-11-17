# Cesta Certa (MVP)

Cadastro de famílias e controle de estoque para uma ONG de bairro (caso fictício de estudo).
Python 3.12, Flask, SQLAlchemy, PostgreSQL (produção) ou SQLite (local), pytest.

## Rodar localmente
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
flask --app run seed                           # itens de demonstração
flask --app run create-user coordenacao_demo   # pede a senha (mín. 8 caracteres)
flask --app run run
```

## Testes
```bash
python -m pytest -v
```

## Variáveis de ambiente (nunca no código)
- `SECRET_KEY`: obrigatória em produção (`FLASK_ENV=production`).
- `DATABASE_URL`: string de conexão do PostgreSQL (ex.: Supabase). Sem ela, usa SQLite local.

## Requisitos atendidos
RF01 cadastro sem duplicidade · RF02 entradas e saídas · RF03 alerta de estoque baixo ·
RNF01 login com hash scrypt, sessão de 30 min e bloqueio após 5 erros ·
RNF02 validação no servidor, consultas parametrizadas, escape de saída, CSRF e CSP.

Não incluídos neste MVP: relatório mensal (RF04), perfis de acesso, modo offline (PWA).
