"""Entregar o resultado ao utilizador: descarregar um PDF ou um ZIP (em streaming), em vez de «abrir a pasta» como a app Windows.

Substitui `os.startfile` (abrir a pasta dos PDFs) e a impressao local: o utilizador descarrega o(s) PDF(s) e imprime onde quiser.
O ZIP gera-se aos bocados, sem o ter inteiro em memoria nem em disco (a webapp tem 512 MB de RAM).
"""
from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

from .motor import nome_seguro

MEDIA_PDF = "application/pdf"
MEDIA_ZIP = "application/zip"
BOCADO = 256 * 1024


class _Fluxo:
    """Destino «sem retrocesso» para o zipfile: junta o que lhe escrevem e entrega-o a quem consome o gerador."""

    def __init__(self):
        self.pedacos: list = []
        self.pos = 0

    def write(self, b) -> int:
        self.pedacos.append(bytes(b))
        self.pos += len(b)
        return len(b)

    def tell(self) -> int:
        return self.pos

    def flush(self) -> None:
        pass

    def levar(self) -> bytes:
        dados, self.pedacos = b"".join(self.pedacos), []
        return dados


def zip_em_streaming(ficheiros: Iterable[Path], comprimir: bool = False) -> Iterator[bytes]:
    """Gera os bytes de um ZIP com os `ficheiros` (so o nome, sem pastas), aos bocados. Por defeito sem compressao: os PDFs ja vao
    comprimidos. Nomes repetidos ficam «nome (2).pdf». Serve diretamente de corpo de uma resposta HTTP em streaming."""
    fluxo = _Fluxo()
    metodo = zipfile.ZIP_DEFLATED if comprimir else zipfile.ZIP_STORED
    usados: set = set()
    with zipfile.ZipFile(fluxo, "w", compression=metodo, allowZip64=True) as zf:
        for caminho in ficheiros:
            caminho = Path(caminho)
            nome, k = caminho.name, 1
            while nome in usados:
                k += 1
                nome = f"{caminho.stem} ({k}){caminho.suffix}"
            usados.add(nome)
            info = zipfile.ZipInfo.from_file(caminho, arcname=nome)
            info.compress_type = metodo
            with caminho.open("rb") as origem, zf.open(info, "w", force_zip64=True) as destino:
                while True:
                    bloco = origem.read(BOCADO)
                    if not bloco:
                        break
                    destino.write(bloco)
                    dados = fluxo.levar()
                    if dados:
                        yield dados
        # (o fim do with escreve o diretorio central)
    dados = fluxo.levar()
    if dados:
        yield dados


@dataclass
class Entrega:
    tipo: str              # "pdf" (um ficheiro, descarrega-se tal e qual) | "zip" (varios)
    nome: str              # nome sugerido para o download
    media_type: str
    ficheiros: list        # caminhos dos PDFs


def entrega(resultados: list, nome_base: str) -> Entrega:
    """O que o utilizador descarrega depois de gerar: o PDF, se so ha um, ou um ZIP com todos. `resultados` = lista de core.Resultado
    (so entram os que passaram na verificacao; se nenhum passou levanta ValueError)."""
    bons = [r.caminho for r in resultados if r.ok]
    if not bons:
        raise ValueError("nenhum PDF verificado para entregar")
    if len(bons) == 1:
        return Entrega("pdf", bons[0].name, MEDIA_PDF, bons)
    base = nome_seguro(nome_base) or "rifas"
    return Entrega("zip", f"{base}.zip", MEDIA_ZIP, bons)


def conteudo_da_entrega(e: Entrega) -> Iterator[bytes]:
    """Os bytes a enviar: o PDF aos bocados, ou o ZIP em streaming."""
    if e.tipo == "zip":
        yield from zip_em_streaming(e.ficheiros)
        return
    with e.ficheiros[0].open("rb") as f:
        while True:
            bloco = f.read(BOCADO)
            if not bloco:
                return
            yield bloco
