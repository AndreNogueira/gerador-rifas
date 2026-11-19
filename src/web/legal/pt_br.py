"""Termos, privacidade e contacto em português do Brasil: derivados de `legal/pt.py` por `core.ptbr` (glossário) e adaptados à lei brasileira onde o texto cita a lei:
a LGPD em vez do RGPD, a ANPD em vez da CNPD e as regras das rifas (sem afirmar nada: quem organiza confirma com a autoridade competente). **Sem revisão jurídica:
um advogado brasileiro tem de ver estas páginas antes de o serviço ser divulgado no Brasil** (`docs/PLANO_PTBR.md`)."""
from core import ptbr

from . import pt

FRASES = ptbr.derivar_tudo(pt.FRASES)
AVISO = ptbr.derivar(pt.AVISO)
TEXTOS = ptbr.derivar_tudo(pt.TEXTOS)

# as rifas e os sorteios: no Brasil as regras são federais e locais e podem ser mais restritivas; o serviço não afirma nada, remete para a autoridade competente
_REGRAS_ANTES = "As rifas, as tômbolas e os sorteios estão sujeitos a regras legais"
for _s in TEXTOS["termos"]["seccoes"]:
    _s["paragrafos"] = [
        ("As rifas e os sorteios com prêmios estão sujeitos a regras legais (por exemplo, autorizações de órgãos públicos e regras para associações) que variam conforme o caso "
         "e que podem ser restritivas. Quem organiza a rifa é o único responsável por consultar a autoridade competente, cumprir a lei, cobrar e entregar os prêmios. "
         "Este serviço não dá aconselhamento jurídico.") if p.startswith(ptbr.derivar(_REGRAS_ANTES)) else p
        for p in _s["paragrafos"]]
