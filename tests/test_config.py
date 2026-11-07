"""Testes de core.config: preferencias (config.json) e pasta de dados. Antes vivia em app.py
(ler_config, gravar_config, App._carregar_config, App._guardar_config)."""
import json
from pathlib import Path

from core import config


# ------------------------------------------------------------------ pasta_de_dados
def test_pasta_de_dados_prioridade(monkeypatch, tmp_path):
    monkeypatch.delenv("RIFAS_DADOS", raising=False)
    assert config.pasta_de_dados(tmp_path / "padrao") == tmp_path / "padrao"
    assert config.pasta_de_dados() == Path.home() / ".gerador-rifas"
    monkeypatch.setenv("RIFAS_DADOS", str(tmp_path / "env"))
    assert config.pasta_de_dados(tmp_path / "padrao") == tmp_path / "env"       # a variavel de ambiente ganha
    monkeypatch.setenv("RIFAS_DADOS", "   ")
    assert config.pasta_de_dados(tmp_path / "padrao") == tmp_path / "padrao"    # vazia = como se nao existisse


def test_nomes_e_constantes():
    assert config.NOME_CONFIG == "config.json" and config.ENV_DADOS == "RIFAS_DADOS"
    assert config.MODOS == ("varios", "unico")


# ------------------------------------------------------------------ ler / gravar
def test_gravar_e_ler(tmp_path):
    f = tmp_path / "sub" / "pasta" / "config.json"
    config.gravar_config(f, {"lingua": "pt", "nome": "Ação ñ"})
    assert f.exists()                                            # cria as pastas todas
    assert config.ler_config(f) == {"lingua": "pt", "nome": "Ação ñ"}
    assert "Ação" in f.read_text(encoding="utf-8")                # ensure_ascii=False
    assert f.read_text(encoding="utf-8").startswith('{\n  "lingua"')   # indent=2


def test_ler_config_tolerante(tmp_path):
    assert config.ler_config(tmp_path / "nao_existe.json") == {}
    (tmp_path / "mau.json").write_text("{isto nao e json", encoding="utf-8")
    assert config.ler_config(tmp_path / "mau.json") == {}
    (tmp_path / "vazio.json").write_text("", encoding="utf-8")
    assert config.ler_config(tmp_path / "vazio.json") == {}


def test_gravar_config_ignora_erros(tmp_path):
    (tmp_path / "ficheiro").write_text("x")
    config.gravar_config(tmp_path / "ficheiro" / "config.json", {"a": 1})        # a «pasta» e um ficheiro: nao rebenta
    assert not (tmp_path / "ficheiro" / "config.json").exists()


# ------------------------------------------------------------------ preferencias
def test_preferencias_vazias():
    assert config.preferencias({}) == {}
    assert config.preferencias({"lingua": "en", "tema": "dark"}) == {}          # lingua e tema tratam-se fora


def test_preferencias_campos_de_texto_sempre_str(tmp_path):
    alg = tmp_path / "alg.pdf"
    alg.write_bytes(b"x")
    cfg = {"algarismos": str(alg), "saida": "C:/out", "inicio": 1, "fim": "5000", "digitos": 4, "max": 500, "margem": 5}
    assert config.preferencias(cfg) == {"algarismos": str(alg), "saida": "C:/out", "inicio": "1", "fim": "5000",
                                        "digitos": "4", "max": "500", "margem": "5"}


def test_preferencias_ignora_vazios_mas_nao_o_zero():
    assert config.preferencias({"saida": "", "inicio": 0, "fim": "", "margem": 0}) == {"inicio": "0", "margem": "0"}
    assert config.preferencias({"saida": None}) == {"saida": "None"}          # quirk: None nao conta como vazio


def test_preferencias_papel_e_modo_validados():
    assert config.preferencias({"papel": "A3", "modo": "unico"}) == {"papel": "A3", "modo": "unico"}
    assert config.preferencias({"papel": "B5", "modo": "outro"}) == {}
    assert config.preferencias({"papel": "a4"}) == {}                         # sensivel a maiusculas


def test_preferencias_esquece_algarismos_que_ja_nao_existem(tmp_path):
    assert config.preferencias({"algarismos": str(tmp_path / "apagado.pdf"), "fim": "9"}) == {"fim": "9"}


# ------------------------------------------------------------------ para_gravar
def test_para_gravar_nunca_inclui_template_nem_nome():
    d = config.para_gravar(lingua="pt", tema="system", algarismos="a.pdf", saida="out", inicio="1", fim="9", digitos="4",
                           max_ficheiro="500", modo="varios", papel="A4", margem="5")
    assert list(d) == ["lingua", "tema", "algarismos", "saida", "inicio", "fim", "digitos", "max", "modo", "papel", "margem"]
    assert "template" not in d and "nome" not in d
    assert d["max"] == "500"
    json.dumps(d)                                              # serializavel


def test_ida_e_volta(tmp_path):
    alg = tmp_path / "alg.png"
    alg.write_bytes(b"x")
    d = config.para_gravar("en", "dark", str(alg), "out", "1", "99", "3", "50", "unico", "Letter", "7")
    f = tmp_path / "c.json"
    config.gravar_config(f, d)
    assert config.preferencias(config.ler_config(f)) == {
        "algarismos": str(alg), "saida": "out", "inicio": "1", "fim": "99", "digitos": "3", "max": "50",
        "margem": "7", "papel": "Letter", "modo": "unico"}
