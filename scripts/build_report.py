"""Gera uma página-resumo em português (report/index.html) a partir do CSV do Locust.

Linguagem acessível (para quem não é técnico) + números-chave + veredito de SLA,
com link para o relatório técnico completo do Locust (report/locust.html).
"""
import csv
import os
from datetime import datetime

REPORT_DIR = "report"
CSV_PATH = os.path.join(REPORT_DIR, "stats_stats.csv")

USERS = os.getenv("LOAD_USERS", "?")
RUNTIME = os.getenv("LOAD_RUNTIME", "?")
SLA_P95_MS = int(os.getenv("SLA_P95_MS", "500"))
SLA_FAIL_PCT = float(os.getenv("SLA_FAIL_PCT", "1"))


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


with open(CSV_PATH, newline="") as f:
    rows = list(csv.DictReader(f))

agg = next(r for r in rows if r["Name"] == "Aggregated")
endpoints = [r for r in rows if r["Name"] != "Aggregated"]

total = int(to_float(agg["Request Count"]))
fails = int(to_float(agg["Failure Count"]))
fail_pct = (fails / total * 100) if total else 0.0
rps = to_float(agg["Requests/s"])
p95 = to_float(agg["95%"])
avg = to_float(agg["Average Response Time"])

ok = (p95 <= SLA_P95_MS) and (fail_pct <= SLA_FAIL_PCT)
verdict = "APROVADO" if ok else "REPROVADO"
verdict_class = "ok" if ok else "fail"
when = datetime.now().strftime("%d/%m/%Y %H:%M")

kpis = [
    (f"{USERS}", "usuários simultâneos", "Pessoas usando o sistema ao mesmo tempo durante o teste."),
    (f"{RUNTIME}", "duração do teste", "Por quanto tempo a carga foi aplicada."),
    (f"{total:,}".replace(",", "."), "requisições feitas", "Total de ações enviadas ao sistema (abrir página, comprar, etc.)."),
    (f"{fails}", "falharam", "Quantas ações deram erro. Quanto mais perto de zero, melhor."),
    (f"{avg:.0f} ms", "tempo médio de resposta", "Quanto o sistema leva, em média, pra responder (ms = milésimos de segundo)."),
    (f"{p95:.0f} ms", "p95 (95% abaixo disso)", "95% das respostas foram mais rápidas que isso. Mede a experiência no pior caso comum."),
    (f"{rps:.1f}/s", "vazão (req. por segundo)", "Quantas ações o sistema consegue atender a cada segundo."),
]

kpi_html = "\n".join(
    f'''<div class="kpi"><div class="n">{v}</div><div class="l">{lab}</div><div class="h">{hint}</div></div>'''
    for v, lab, hint in kpis
)

rows_html = "\n".join(
    f'''<tr><td class="mono">{r["Type"]}</td><td>{r["Name"]}</td>
        <td class="num">{int(to_float(r["Request Count"]))}</td>
        <td class="num">{int(to_float(r["Failure Count"]))}</td>
        <td class="num">{to_float(r["Average Response Time"]):.0f} ms</td>
        <td class="num">{to_float(r["95%"]):.0f} ms</td></tr>'''
    for r in endpoints
)

verdict_text = (
    f"O sistema aguentou <b>{USERS} usuários ao mesmo tempo</b> por <b>{RUNTIME}</b>, "
    f"respondendo <b>{total:,}</b>".replace(",", ".") +
    f" ações com <b>{fails} falha(s)</b> ({fail_pct:.2f}%) e tempo de resposta "
    f"(p95) de <b>{p95:.0f} ms</b> — dentro do limite de qualidade (SLA)."
    if ok else
    f"O sistema <b>estourou o limite de qualidade (SLA)</b>: "
    f"p95 de {p95:.0f} ms (meta &lt; {SLA_P95_MS} ms) e {fail_pct:.2f}% de falhas "
    f"(meta &lt; {SLA_FAIL_PCT}%). Indica que, sob essa carga, o desempenho precisa de atenção."
)

CSS = """
*{box-sizing:border-box}
body{margin:0;background:#eef3f6;color:#15242e;font-family:-apple-system,"Segoe UI",system-ui,Roboto,sans-serif;line-height:1.55}
.wrap{max-width:900px;margin:0 auto;padding:32px 20px 60px}
h1{font-size:26px;margin:0 0 4px}
.sub{color:#5a7180;font-size:14px;margin:0 0 24px}
.verdict{display:flex;gap:14px;align-items:flex-start;border-radius:14px;padding:18px 20px;margin:0 0 24px;border:1px solid}
.verdict.ok{background:#e4f6ec;border-color:#2e9e6b}
.verdict.fail{background:#fde6e8;border-color:#c0392b}
.verdict .tag{font-weight:800;font-size:13px;letter-spacing:.5px;padding:5px 11px;border-radius:999px;color:#fff;white-space:nowrap}
.verdict.ok .tag{background:#2e9e6b}
.verdict.fail .tag{background:#c0392b}
.verdict p{margin:0;font-size:14.5px}
.intro{background:#fff;border:1px solid #dce5ea;border-radius:12px;padding:16px 18px;margin:0 0 24px;font-size:14.5px;color:#36505d}
.intro b{color:#0d7f93}
h2{font-size:16px;margin:28px 0 12px;color:#0d6274}
.kpis{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}
.kpi{background:#fff;border:1px solid #dce5ea;border-radius:12px;padding:14px 16px}
.kpi .n{font-size:24px;font-weight:800;color:#0d7f93;font-variant-numeric:tabular-nums}
.kpi .l{font-size:13px;font-weight:600;margin-top:2px}
.kpi .h{font-size:12px;color:#6a828f;margin-top:5px}
table{width:100%;border-collapse:collapse;background:#fff;border:1px solid #dce5ea;border-radius:12px;overflow:hidden;font-size:13.5px}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid #eef2f5}
th{background:#f4f8fa;font-size:11.5px;text-transform:uppercase;letter-spacing:.04em;color:#6a828f}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.mono{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12px;color:#0d7f93}
.tablewrap{overflow-x:auto}
.btn{display:inline-block;margin-top:20px;background:#103a4e;color:#fff;text-decoration:none;padding:11px 18px;border-radius:10px;font-size:14px;font-weight:600}
.btn:hover{background:#0d6274}
.glossary{font-size:13.5px;color:#4a6472}
.glossary li{margin:5px 0}
.glossary b{color:#15242e}
footer{margin-top:36px;padding-top:16px;border-top:1px solid #dce5ea;font-size:12px;color:#8097a3}
"""

HTML = f"""<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Relatório de Teste de Carga</title><style>{CSS}</style></head>
<body>
<div class="wrap">
  <h1>⚡ Relatório de Teste de Carga</h1>
  <p class="sub">Demo Store API &middot; gerado em {when}</p>

  <div class="verdict {verdict_class}">
    <span class="tag">{"✅ " if ok else "❌ "}{verdict}</span>
    <p>{verdict_text}</p>
  </div>

  <div class="intro">
    <b>O que é um teste de carga?</b> É simular <b>muitos usuários usando o sistema ao mesmo tempo</b>
    para descobrir se ele aguenta o tranco — se continua <b>rápido</b> e <b>sem erros</b> sob pressão,
    antes dos usuários reais chegarem. Abaixo, o resultado em números simples.
  </div>

  <h2>📊 Resumo em números</h2>
  <div class="kpis">
    {kpi_html}
  </div>

  <h2>🧭 O que cada número quer dizer</h2>
  <ul class="glossary">
    <li><b>Tempo de resposta</b> — quanto o sistema demora pra responder. Menor = mais rápido (em ms, milésimos de segundo).</li>
    <li><b>p95</b> — 95% das respostas foram mais rápidas que esse valor. Mostra como é a experiência no "pior caso comum", ignorando picos raros.</li>
    <li><b>Vazão</b> — quantas ações por segundo o sistema consegue atender. Maior = aguenta mais gente.</li>
    <li><b>SLA</b> — o "contrato de qualidade": metas que o sistema tem que cumprir (aqui: p95 abaixo de {SLA_P95_MS} ms e menos de {SLA_FAIL_PCT}% de erros). Se estourar, o teste reprova.</li>
  </ul>

  <h2>🔎 Detalhe por rota testada</h2>
  <div class="tablewrap">
  <table>
    <thead><tr><th>Método</th><th>Rota</th><th class="num">Requisições</th><th class="num">Falhas</th><th class="num">Tempo médio</th><th class="num">p95</th></tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
  </div>

  <a class="btn" href="locust.html">🔧 Ver relatório técnico completo (Locust) →</a>

  <footer>
    Teste executado com <b>Locust</b> contra uma API FastAPI própria (ambiente de teste). &middot;
    Projeto de portfólio de QA &middot; Mateus Cerqueira
  </footer>
</div>
</body>
</html>
"""

with open(os.path.join(REPORT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"index.html gerado | veredito: {verdict} | p95={p95:.0f}ms fails={fails} rps={rps:.1f}")
