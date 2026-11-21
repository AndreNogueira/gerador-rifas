"""O crédito às bibliotecas de ícones do preçário que o exigem (Twemoji, OpenMoji) na Política de privacidade, nas 22 línguas."""
import pytest

pytest.importorskip("fastapi", reason="a webapp precisa do grupo `web` (uv sync)")
from core import i18n
from web import legal_icones, textos_legais


def test_todas_as_linguas_tem_o_texto():
    assert set(legal_icones.TEXTOS) == set(i18n.LINGUAS)                 # uma língua nova obriga a escrever esta secção


@pytest.mark.parametrize("lg", list(i18n.LINGUAS))
def test_a_privacidade_credita_o_twemoji_e_o_openmoji_em_todas_as_linguas(lg):
    seccao = textos_legais.privacidade(lg)["seccoes"][-3]                # icones vem antes de medicoes (sempre -2) e de opiniao (sempre -1)
    assert seccao["titulo"] == legal_icones.TEXTOS[lg]["titulo"]
    texto = seccao["paragrafos"][0]
    assert "Twemoji" in texto and "OpenMoji" in texto and "CC BY" in texto


def test_noto_e_fluent_nao_sao_mencionados_por_obrigacao_so_por_transparencia():
    """Nem o Noto Emoji nem o Fluent Emoji exigem crédito (ver core.precario_catalogo.FONTES_EXTRA): se um dia passarem a exigir,
    esta secção tem de ser atualizada para os citar como "que exigem" também."""
    from core import precario_catalogo as cat
    assert not cat.FONTES_EXTRA["fluent"].credito
