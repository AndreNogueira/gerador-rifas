"""`python -m src.web`: arranca a webapp (porta em PORT, por omissao 8080).

Este modulo tem de ficar LEVE: o processo do motor (multiprocessing, «spawn») volta a importar o modulo principal, e nao queremos
o FastAPI nem o uvicorn carregados duas vezes (512 MB de RAM). Por isso as importacoes pesadas estao dentro de `iniciar()`.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))     # src/ no caminho: `import core`


def iniciar() -> None:
    import uvicorn

    from . import config
    from .app import criar_app

    # O IP do cliente (para os limites por IP) vem em X-Forwarded-For quando se esta atras do proxy do Render. So se confia nesse
    # cabecalho se o pedido vem de uma rede privada (o proxy): com "*" qualquer cliente poderia inventar o IP e fugir aos limites.
    uvicorn.run(criar_app(), host=config.host(), port=config.porta(), log_level="info", proxy_headers=True,
                forwarded_allow_ips=config.proxies_de_confianca())


if __name__ == "__main__":
    iniciar()
