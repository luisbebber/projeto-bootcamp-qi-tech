# Bank as a Service

Projeto final do Bootcamp: um Bank as a Service feito com 3 APIs neste repositório (Python, FastAPI, PostgreSQL e Docker).

| API | Papel |
|---|---|
| `client-api` | Cadastra as operações das empresas que contratam o BaaS (um `client` = uma operação de uma empresa). |
| `fee-api` | Guarda os valores de taxa de cada empresa, registra uma taxa por operação e fecha a cobrança mensal. |
| `account-api` | Contas, depósito, saque, transferência entre contas da mesma empresa, saldo e extrato paginado. |

As taxas são cobradas da empresa, nunca do usuário final.

## Como rodar

Cada API é independente: tem o próprio `docker-compose.yml`, o próprio Postgres e o próprio MockServer, e conversa com as outras apenas através do MockServer. Por isso usam as mesmas portas (`3000` API, `5432` banco, `1080` mock) e sobem uma de cada vez.

Pré-requisitos: Docker com Docker Compose, e Python 3.11+ para os testes.

```bash
cd account-api            # ou client-api, fee-api
docker compose up --build
```

Nenhuma variável de ambiente é obrigatória: o compose tem valores padrão. O `.env.example` de cada API lista os nomes. O token padrão é `default_token`.


## Como rodar os testes

Os testes são de caixa-preta. Com a API (e o mock) no ar:

```bash
cd account-api            # a mesma pasta cujo compose está rodando
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```
