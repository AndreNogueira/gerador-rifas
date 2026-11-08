"""Preferencias do utilizador (ficheiro config.json) e pasta de dados.

Extraido de app.py (ler_config, gravar_config, App._carregar_config e _guardar_config). Sem Tkinter e sem nada do Windows:
a pasta de dados vem da variavel de ambiente RIFAS_DADOS ou do valor por defeito que a aplicacao indica (a app
Windows passa %APPDATA%\\GeradorRifas).

O template e o nome dos ficheiros NUNCA se guardam (cada rifa tem os seus); o ficheiro dos algarismos guarda-se so como
caminho e esquece-se se o ficheiro ja nao existe.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from .motor import PAPEIS

ENV_DADOS = "RIFAS_DADOS"            # variavel de ambiente: pasta onde se guarda o config.json
NOME_CONFIG = "config.json"
MODOS = ("varios", "unico")
VISUAIS_CONFIG = ("auto", "premiado", "natal")           # o visual da app Windows (ver core.tema)
# campos de texto guardados tal e qual (chave do config.json == chave devolvida por preferencias())
CAMPOS_DE_TEXTO = ("algarismos", "saida", "inicio", "fim", "digitos", "max", "margem")


def pasta_de_dados(por_defeito: Path | None = None) -> Path:
    """RIFAS_DADOS, se estiver definida; senao `por_defeito`; senao ~/.gerador-rifas."""
    env = os.environ.get(ENV_DADOS, "").strip()
    if env:
        return Path(env)
    return Path(por_defeito) if por_defeito is not None else Path.home() / ".gerador-rifas"


def ler_config(ficheiro: Path) -> dict:
    """Le o JSON; qualquer problema (nao existe, corrompido, nao e um objeto...) da {} - comportamento original:
    so falha o que nao e um dict mais tarde."""
    try:
        return json.loads(Path(ficheiro).read_text(encoding="utf-8"))
    except Exception:
        return {}


def gravar_config(ficheiro: Path, d: dict) -> None:
    """Cria a pasta se for preciso e grava; qualquer erro e ignorado (nao e grave perder as preferencias)."""
    try:
        ficheiro = Path(ficheiro)
        ficheiro.parent.mkdir(parents=True, exist_ok=True)
        ficheiro.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def preferencias(cfg: dict, caminhos: bool = True) -> dict:
    """Valores a pre-preencher a partir do config: so as chaves que tem valor (vazio ou ausente = nao mexer).
    Chaves de texto: algarismos, saida, inicio, fim, digitos, max, margem (sempre como str); `papel` so se for um papel
    conhecido; `modo` so se for «varios» ou «unico»; o caminho dos algarismos desaparece se o ficheiro ja nao existe.
    Com `caminhos=False` (webapp, preferencias vindas do browser) nunca se devolvem `algarismos` nem `saida`."""
    saida: dict = {}
    for chave in CAMPOS_DE_TEXTO:
        if cfg.get(chave, "") != "":
            saida[chave] = str(cfg[chave])
    if cfg.get("visual") in VISUAIS_CONFIG:
        saida["visual"] = cfg["visual"]
    if cfg.get("papel") in PAPEIS:
        saida["papel"] = cfg["papel"]
    if cfg.get("modo") in MODOS:
        saida["modo"] = cfg["modo"]
    if saida.get("algarismos") and not Path(saida["algarismos"]).exists():
        del saida["algarismos"]
    if not caminhos:            # webapp: o ficheiro e a pasta ficam no computador do utilizador, o servidor nao os conhece
        saida.pop("algarismos", None)
        saida.pop("saida", None)
    return saida


def para_gravar(lingua: str, tema: str, algarismos: str, saida: str, inicio: str, fim: str, digitos: str, max_ficheiro: str,
                modo: str, papel: str, margem: str, visual: str = "") -> dict:
    """O que se escreve no config.json (e nada mais: sem template, sem nome dos ficheiros). `visual` so se escreve se tem valor."""
    d = {"lingua": lingua, "tema": tema, "algarismos": algarismos, "saida": saida, "inicio": inicio, "fim": fim,
         "digitos": digitos, "max": max_ficheiro, "modo": modo, "papel": papel, "margem": margem}
    if visual:
        d["visual"] = visual
    return d
