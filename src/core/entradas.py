"""Entradas que chegam como bytes (upload na webapp) em vez de caminhos: validacao do tipo real e ficheiros temporarios.

O motor trabalha com ficheiros (`Path`); aqui os bytes recebidos passam a ficheiros temporarios com um nome seguro, escolhido
por nos (nunca o caminho do cliente), e apagam-se no fim. Nao ha limites de tamanho aqui: aplicam-se na camada HTTP.
"""
from __future__ import annotations

import contextlib
import tempfile
from pathlib import Path
from typing import Callable

from .motor import ErroAlgarismos, ErroRifas, Preparado, _sem_log, analisar_template, nome_seguro, preparar

# assinaturas dos ficheiros aceites (o inicio dos bytes; a extensao do nome que o cliente da nao conta)
ASSINATURAS = ((b"%PDF-", "pdf"), (b"\x89PNG\r\n\x1a\n", "png"), (b"\xff\xd8\xff", "jpg"))


def detetar_tipo(dados: bytes) -> str | None:
    """'pdf' | 'png' | 'jpg' pelo inicio dos bytes, ou None se nao for nenhum destes."""
    for assinatura, tipo in ASSINATURAS:
        if dados.startswith(assinatura):
            return tipo
    return None


def nome_de_upload(nome: str, tipo: str, por_defeito: str = "ficheiro") -> str:
    """Nome seguro para o ficheiro temporario: o do cliente sem caracteres perigosos nem pastas, com a extensao do tipo REAL."""
    base = nome_seguro(Path(str(nome).replace("\\", "/")).name)           # so o ultimo componente, sem /, \ , :, etc.
    stem = Path(base).stem if base else ""
    return f"{stem or por_defeito}.{tipo}"


@contextlib.contextmanager
def ficheiro_temporario(dados: bytes, nome: str, pasta: Path | None = None):
    """Escreve `dados` num ficheiro temporario chamado `nome` (use `nome_de_upload`) e devolve o Path; apaga tudo no fim."""
    with tempfile.TemporaryDirectory(prefix="rifas_", dir=str(pasta) if pasta else None) as d:
        destino = Path(d) / nome
        destino.write_bytes(dados)
        yield destino


def preparar_de_bytes(template: bytes, algarismos: bytes | None, nome_template: str = "template.pdf",
                      nome_algarismos: str = "algarismos", log: Callable[[str], None] = _sem_log) -> Preparado:
    """`core.preparar` para ficheiros recebidos como bytes. O template tem de ser PDF; os algarismos PDF, PNG ou JPG (o tipo
    decide-se pelos bytes, nao pelo nome). Erros: os de `preparar`; tipo errado -> `err_abrir_template` (template) ou
    `err_formato` (algarismos). O `Preparado` fica independente dos temporarios (que ja nao existem)."""
    if detetar_tipo(template) != "pdf":
        raise ErroRifas("err_abrir_template", erro="not a PDF file")
    nome_t = nome_de_upload(nome_template, "pdf", "template")
    tipo_a = detetar_tipo(algarismos) if algarismos is not None else None
    if algarismos is not None and tipo_a is None:
        # o template e valido: devolve-se o erro dos algarismos com a info do template, como faz o preparar()
        with ficheiro_temporario(template, nome_t) as tpl:
            info = analisar_template(tpl)
        info.caminho = Path(nome_t)
        raise ErroAlgarismos("err_formato", info)
    nome_a = nome_de_upload(nome_algarismos, tipo_a, "algarismos") if tipo_a else None
    with ficheiro_temporario(template, nome_t) as tpl:
        try:
            if algarismos is None:
                prep = preparar(tpl, None, log)
            else:
                if nome_a == nome_t:                  # nunca deixar os algarismos escreverem por cima do template
                    nome_a = "alg_" + nome_a
                alg = tpl.parent / nome_a
                alg.write_bytes(algarismos)
                prep = preparar(tpl, alg, log)
        except ErroAlgarismos as e:
            e.info.caminho = Path(nome_t)             # nao deixar o caminho do temporario (que vai desaparecer) na info
            raise
    prep.template = Path(nome_t)
    prep.info.caminho = Path(nome_t)
    return prep
