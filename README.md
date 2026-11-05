<div align="center">

# ⚡ load-tests-locust

**Testes de Carga / Performance** &nbsp;·&nbsp; Python &nbsp;·&nbsp; Locust &nbsp;·&nbsp; SLA gate no CI

[![Load Test](https://github.com/MateusCerqueiraG/load-tests-locust/actions/workflows/load.yml/badge.svg)](https://github.com/MateusCerqueiraG/load-tests-locust/actions/workflows/load.yml)
&nbsp;
[![Relatório Locust](https://img.shields.io/badge/📊_Relatório-Locust_ao_vivo-5fd0e6?style=flat&labelColor=103a4e)](https://mateuscerqueirag.github.io/load-tests-locust/)

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Locust](https://img.shields.io/badge/Locust-2.x-2EAD33?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-alvo-009688?logo=fastapi&logoColor=white)

</div>

---

Testes de **carga e performance** com **Locust**: modela o comportamento de usuários sob tráfego concorrente, mede **vazão, percentis e taxa de erro**, e **reprova o build** quando o desempenho estoura o orçamento (SLA) — tudo rodando em **CI** com relatório HTML publicado.

> 🎯 **Alvo sob teste:** uma **API FastAPI própria** (`app/main.py`), que o repositório sobe localmente. Teste de carga **só se faz contra a sua própria instância** — nunca contra o serviço público de um terceiro (seria abuso). Por isso o alvo vem junto.

## ✅ O que a suíte faz

| Item | Detalhe |
|:--|:--|
| 👤 **Perfil de carga** | usuário que navega no catálogo e às vezes compra (mais leitura que escrita) |
| 🌐 **Endpoints** | `GET /products` · `GET /products/[id]` · `POST /orders` · `GET /health` |
| 📈 **Métricas** | vazão (req/s), tempos médios e **percentis (p95)**, taxa de erro |
| 🚦 **SLA gate** | falha o CI se **p95 > 500 ms** ou **erro > 1%** (validado em código) |

<div align="center">

**50 usuários &nbsp;·&nbsp; 30 s &nbsp;·&nbsp; SLA validado no pipeline**

</div>

## 🧰 Stack & práticas

- 🐍 **Locust 2.x** — perfil de carga como código (`HttpUser`, `@task` com pesos)
- 🚦 **SLA em código** — event hook `quitting` checa p95 e fail-ratio e define o exit code
- 🎯 **Alvo self-contained** — FastAPI subida pelo próprio CI (teste ético)
- ⚙️ **CI** — GitHub Actions roda a carga e **publica o relatório HTML** do Locust

## 📁 Estrutura

```
app/main.py              # API-alvo (FastAPI, em memória): products / orders / health
locustfile.py            # perfil de carga (tasks com pesos) + gate de SLA
.github/workflows/load.yml
requirements.txt
```

## ▶️ Como rodar localmente

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1) sobe a API-alvo
uvicorn app.main:app --port 8000

# 2) em outro terminal: modo visual (abre o painel do Locust em http://localhost:8089)
locust -f locustfile.py --host http://localhost:8000

# ou headless, igual ao CI:
locust -f locustfile.py --headless --host http://localhost:8000 \
  --users 50 --spawn-rate 10 --run-time 30s --html report/index.html
```

## 📊 Relatório Locust

Publicado automaticamente a cada push na `main`:

### 👉 **[mateuscerqueirag.github.io/load-tests-locust](https://mateuscerqueirag.github.io/load-tests-locust/)**

---

<div align="center">
<sub>Projeto de portfólio · foco em teste de carga com Locust · alvo próprio (FastAPI), nunca serviço de terceiro</sub>
</div>
