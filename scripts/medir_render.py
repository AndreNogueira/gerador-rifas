"""Mede o tempo que o serviço REAL (Render) demora a pré-visualizar e a gerar N números, com o que há em `tests/fixtures`.

Para repetir quando mudar o plano do Render, o motor ou `MAX_NUMEROS` (resultados e como os ler: `docs/MEDICOES.md`). Só usa a biblioteca standard.

    uv run python scripts/medir_render.py --url https://gerador-rifas.onrender.com --tamanhos 500 2000 5000 [--saida medicoes.json]

Notas:
 - O serviço gratuito corre UMA geração de cada vez para toda a gente: se alguém estiver a gerar, o pedido recebe «ocupado» e o script espera e tenta outra vez.
 - A primeira chamada pode apanhar o serviço a dormir (cold start): mede-se à parte (`acordar_s`).
 - Cada medição cria uma sessão, descarrega o resultado (só se conta o tamanho) e apaga a sessão. Nada fica no servidor.
 - Gera carga de verdade: usar tamanhos moderados (o teto do servidor é `MAX_NUMEROS`) e fora de horas de utilização.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
TERMINAIS = {"ok", "erros", "cancelado", "falhou"}


class Cliente:
    def __init__(self, base: str, lingua: str = "pt"):
        self.base = base.rstrip("/")
        self.lingua = lingua

    def pedir(self, metodo: str, caminho: str, corpo: bytes | None = None, json_: dict | None = None, tipo: str = "application/octet-stream",
              timeout: float = 300.0, bruto: bool = False):
        cab = {"X-Lingua": self.lingua, "User-Agent": "medir-render/1 (medicao do proprio dono)"}
        if json_ is not None:
            corpo, tipo = json.dumps(json_).encode(), "application/json"
        if corpo is not None:
            cab["Content-Type"] = tipo
        req = urllib.request.Request(self.base + caminho, data=corpo, method=metodo, headers=cab)
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                dados = r.read()
                ms = (time.perf_counter() - t0) * 1000
                return r.status, (dados if bruto else (json.loads(dados) if dados else {})), ms
        except urllib.error.HTTPError as e:
            dados = e.read()
            try:
                return e.code, json.loads(dados), (time.perf_counter() - t0) * 1000
            except ValueError:
                return e.code, {"detail": dados[:120].decode("utf-8", "replace")}, (time.perf_counter() - t0) * 1000


def acordar(c: Cliente) -> float:
    """Segundos até o serviço responder a /health (o cold start, se estava a dormir)."""
    t0 = time.perf_counter()
    for _ in range(40):
        try:
            s, _, _ = c.pedir("GET", "/health", timeout=30)
            if s == 200:
                break
        except OSError:
            time.sleep(3)
    return round(time.perf_counter() - t0, 2)


def medir(c: Cliente, n: int, modo: str = "unico", espera_max_s: float = 900.0, template: str = "template_exemplo.pdf", algarismos: str = "digitos_exemplo.pdf") -> dict:
    s, sessao, _ = c.pedir("POST", "/api/sessoes")
    if s != 201:
        return {"n": n, "erro": f"criar sessao: {s} {sessao.get('detail', '')}"}
    sid = sessao["sessao"]
    r: dict = {"n": n, "modo": modo, "template": template}
    try:
        _, _, r["upload_template_ms"] = c.pedir("PUT", f"/api/sessoes/{sid}/template", (FIXTURES / template).read_bytes())
        s, sess, r["upload_algarismos_ms"] = c.pedir("PUT", f"/api/sessoes/{sid}/algarismos", (FIXTURES / algarismos).read_bytes())
        if not sess.get("pronto"):
            return {**r, "erro": "template/algarismos nao ficaram prontos"}
        campos = {"nome": "Medicao", "inicio": "1", "fim": str(n), "digitos": str(max(4, len(str(n)))), "modo": modo, "max_ficheiro": "300"}
        _, _, r["calcular_ms"] = c.pedir("POST", f"/api/sessoes/{sid}/calcular", json_=campos)
        s, _, r["previa_ms"] = c.pedir("POST", f"/api/sessoes/{sid}/previa", json_=campos)
        r["previa_estado"] = s
        t_total = time.perf_counter()
        while True:                                                   # «ocupado» (outra geracao a decorrer): espera e tenta outra vez
            s, resp, _ = c.pedir("POST", f"/api/sessoes/{sid}/gerar", json_=campos)
            if s == 202:
                break
            if s in (409, 429, 503) and time.perf_counter() - t_total < espera_max_s:
                time.sleep(5)
                continue
            return {**r, "erro": f"gerar: {s} {resp.get('detail', '')}"}
        t_gerar = time.perf_counter()
        feitas = 0
        while time.perf_counter() - t_gerar < espera_max_s:
            _, t, _ = c.pedir("GET", f"/api/sessoes/{sid}/trabalho")
            feitas = t.get("feitas", feitas)
            if t.get("estado") in TERMINAIS:
                r["estado"] = t["estado"]
                break
            time.sleep(0.25)
        else:
            r["estado"] = "tempo_do_script"
        r["gerar_s"] = round(time.perf_counter() - t_gerar, 2)
        r["numeros_por_s"] = round(n / r["gerar_s"], 1) if r["gerar_s"] else None
        if r.get("estado") in ("ok", "erros"):
            s, dados, r["descarregar_ms"] = c.pedir("GET", f"/api/sessoes/{sid}/descarregar", bruto=True)
            r["tamanho_mb"] = round(len(dados) / 1048576, 2) if s == 200 else None
        return r
    finally:
        c.pedir("DELETE", f"/api/sessoes/{sid}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--url", required=True, help="o endereço do serviço (sem predefinição, para não medir produção por engano)")
    ap.add_argument("--tamanhos", type=int, nargs="+", default=[500, 2000, 5000])
    ap.add_argument("--repeticoes", type=int, default=1)
    ap.add_argument("--modo", choices=["unico", "varios"], default="unico")
    ap.add_argument("--template", default="template_exemplo.pdf", help="um PDF de tests/fixtures (o ritmo depende de quantas rifas ha por pagina)")
    ap.add_argument("--algarismos", default="digitos_exemplo.pdf", help="o PDF/PNG dos algarismos 0-9 desse template")
    ap.add_argument("--saida", help="escreve o resultado em JSON")
    a = ap.parse_args()
    c = Cliente(a.url)
    resultado = {"url": a.url, "quando": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "acordar_s": acordar(c), "medicoes": []}
    s, saude, _ = c.pedir("GET", "/health")
    resultado["versao"] = saude.get("versao")
    print(f"serviço {a.url} v{resultado['versao']} (acordou em {resultado['acordar_s']} s)")
    for n in a.tamanhos:
        for _ in range(a.repeticoes):
            m = medir(c, n, a.modo, template=a.template, algarismos=a.algarismos)
            resultado["medicoes"].append(m)
            print(json.dumps(m, ensure_ascii=False))
    ok = [m for m in resultado["medicoes"] if m.get("estado") == "ok"]
    if ok:
        resultado["numeros_por_s_mediana"] = round(statistics.median(m["numeros_por_s"] for m in ok), 1)
        print(f"mediana: {resultado['numeros_por_s_mediana']} números/s")
    if a.saida:
        Path(a.saida).write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if len(ok) == len(resultado["medicoes"]) else 1


if __name__ == "__main__":
    sys.exit(main())
