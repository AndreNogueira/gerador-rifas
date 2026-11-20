"""A aplicacao FastAPI: a API (`/api`), `/health` e o frontend compilado (ficheiros estaticos, com *fallback* para o index.html).

So chama `core` (um teste proibe aqui imports de pypdf/PIL/Tk). O motor corre noutro processo (`trabalhos.Motor`).
O servico e PUBLICO e sem palavra-passe: ver `limites.py` e `config.py` para as defesas.
"""
from __future__ import annotations

import asyncio
import contextlib
import mimetypes
import os
import time
from pathlib import Path
from zoneinfo import ZoneInfo

from core import i18n
from core.armazenamento import ArmazenamentoLocal
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response as RespostaSimples
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import VERSAO, admin, api_v1, changelog, config, guias, observabilidade, rotas, rotas_ajuda, rotas_editor, rotas_galeria, rotas_listas, rotas_opiniao, rotas_precario, rotas_vales, rotas_verificar, seo, textos_legais
from .chaves_api import Chaves
from .assets_remotos import AssetsRemotos
from .limites import Limitador
from . import alertas, auditoria, copia, historico, indexnow, objetivos, relatorio, relatorio_periodo, seo_textos
from .manter_acordado import ciclo as ciclo_acordado
from .metricas import Metricas, caminho_por_defeito, dispositivo
from .modelos import ErroApi
from .opiniao import Comentarios
from .partilhas import Partilhas
from .rotas import Servico
from .seo_bd import SeoBd
from .sessoes import Sessoes
from .sistema import Observador
from .trabalhos import Motor


_NAO_SERVIR = {".map", ".br", ".gz"}          # mapas e versoes comprimidas: so se entregam como `Content-Encoding` do original


def _aceita(accept_encoding: str, nome: str) -> bool:
    """Se o `Accept-Encoding` aceita a codificacao `nome` (respeita `;q=0`)."""
    for parte in accept_encoding.split(","):
        cod, _, resto = parte.strip().partition(";")
        if cod.strip().lower() != nome:
            continue
        q = "1"
        resto = resto.strip()
        if resto.startswith("q="):
            q = resto[2:].strip()
        try:
            return float(q) > 0
        except ValueError:
            return False
    return False


# Os tipos dos ficheiros que o site serve, FIXOS e iguais em todos os sistemas: o `mimetypes` do Python le o registo do Windows (onde `.js` e `application/javascript` e `.mjs` e
# `text/plain`), e com `nosniff` um tipo errado impede o browser de executar o ficheiro. Em Linux (o Render) ja saem certos; assim tambem saem a correr no Windows.
for _tipo, _extensao in (("text/javascript", ".js"), ("text/javascript", ".mjs"), ("text/css", ".css"), ("application/manifest+json", ".webmanifest"), ("font/woff2", ".woff2"),
                         ("font/woff", ".woff"), ("font/ttf", ".ttf"), ("image/webp", ".webp"), ("image/svg+xml", ".svg"), ("application/json", ".json"), ("text/plain", ".txt")):
    mimetypes.add_type(_tipo, _extensao)

# Cabecalhos de seguranca em TODA a resposta. `nosniff`: o browser respeita o Content-Type (um ficheiro com o tipo errado deixa de se executar: `tests/test_web_cabecalhos.py`
# verifica o de cada ficheiro do `dist`); `SAMEORIGIN`: so este site se desenha dentro de uma `<iframe>` (a pre-visualizacao do PDF); a `Permissions-Policy` fecha o que o site
# nunca usa (nao lista o que os anuncios precisam); o HSTS so com HTTPS e sem `includeSubDomains`/`preload` (o dominio `onrender.com` nao e nosso). Sem CSP por agora:
# os anuncios (AdSense), o PDF.js e os estilos «inline» pedem uma politica medida com cuidado, e uma so de relatorio, sem para onde enviar os relatorios, nao faz nada.
CABECALHOS_SEGURANCA = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Frame-Options": "SAMEORIGIN",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}
HSTS = "max-age=31536000"


def _enviar(alvo: Path, request: Request, cabecalhos: dict[str, str]) -> FileResponse:
    """O ficheiro, ou a sua versao `.br`/`.gz` se existir e o browser a aceitar (nunca re-comprime: so entrega)."""
    media = mimetypes.guess_type(alvo.name)[0]
    ae = request.headers.get("accept-encoding", "")
    tem_comprimidos = False
    for codificacao, extensao in (("br", ".br"), ("gzip", ".gz")):
        comprimido = alvo.with_name(alvo.name + extensao)
        if comprimido.is_file():
            tem_comprimidos = True
            if _aceita(ae, codificacao):
                return FileResponse(comprimido, media_type=media, headers={**cabecalhos, "Content-Encoding": codificacao, "Vary": "Accept-Encoding"})
    return FileResponse(alvo, headers={**cabecalhos, **({"Vary": "Accept-Encoding"} if tem_comprimidos else {})})


class Lingua(BaseModel):
    codigo: str
    nome: str


class Linguas(BaseModel):
    por_defeito: str          # a lingua do browser (Accept-Language), ou ingles
    linguas: list[Lingua]


class Textos(BaseModel):
    lingua: str
    textos: dict[str, str]    # chave -> texto, com {parametros} por substituir no browser


class Saude(BaseModel):
    estado: str
    versao: str


class SeccaoChangelog(BaseModel):
    titulo: str
    itens: list[str]


class EntradaChangelog(BaseModel):
    versao: str
    data: str
    seccoes: list[SeccaoChangelog]


class Changelog(BaseModel):
    entradas: list[EntradaChangelog]


class SeccaoTexto(BaseModel):
    titulo: str
    paragrafos: list[str]


class PaginaTexto(BaseModel):
    titulo: str
    aviso: str
    seccoes: list[SeccaoTexto]


class PassoGuia(BaseModel):
    titulo: str
    texto: str


class GuiaNaLista(BaseModel):
    nome: str
    caminho: str
    titulo: str
    resumo: str


class ListaGuias(BaseModel):
    guias: list[GuiaNaLista]


class GuiaTexto(BaseModel):
    titulo: str
    intro: str
    passos: list[PassoGuia]
    dicas: list[str]
    fim: str


class Publico(BaseModel):
    donativo_url: str          # vazio = sem botao de donativo
    contacto: bool             # ha um e-mail publico configurado (o endereco so aparece na pagina «Contacto»)
    qr: bool = False           # o servidor tem a chave que assina os QR dos bilhetes (VERIFICACAO_CHAVE)
    anuncios_cliente: str = ""  # identificador da AdSense (ca-pub-…): vazio = sem anuncios (ADSENSE_CLIENTE)
    anuncios_slot: str = ""     # bloco de anuncios: vazio = o script carrega-se mas nao se mostra nenhum bloco (ADSENSE_SLOT)
    partilha_editor: bool = False   # o editor pode partilhar desenhos por ligacao (so com DATABASE_URL)
    problemas: bool = False         # «Reportar problema» esta ligado (GITHUB_ISSUES_TOKEN e GITHUB_REPO)


async def _limpeza_periodica(servico: Servico, cada_s: float) -> None:
    """Apaga as sessoes inativas (e os seus ficheiros) de tempos a tempos."""
    while True:
        await asyncio.sleep(cada_s)
        with contextlib.suppress(Exception):
            servico.sessoes.limpar()


async def _amostrar(servico: Servico, cada_s: float) -> None:
    """De `cada_s` em `cada_s` segundos: uma amostra do sistema (CPU, memoria, disco), os reinicios do motor e o buffer para o disco."""
    anteriores = servico.motor.reinicios
    while True:
        with contextlib.suppress(Exception):
            d = await asyncio.to_thread(servico.observador.ler, len(servico.sessoes), servico.motor.geracao is not None, servico.motor.reinicios)
            for _ in range(servico.motor.reinicios - anteriores):
                servico.metricas.evento("motor_reiniciado")
            anteriores = servico.motor.reinicios
            servico.metricas.amostrar(d["cpu"], d["mem_servidor_mb"], d["mem_motor_mb"], d["mem_contentor_mb"], d["disco_usado_mb"],
                                      d["sessoes_ativas"], int(d["geracao_em_curso"]))
            await asyncio.to_thread(servico.metricas.descarregar_periodico)
        await asyncio.sleep(cada_s)


async def _relatorio_diario(servico: Servico, cada_s: float) -> None:
    """De poucos em poucos minutos, depois da meia-noite: grava o resumo de ontem no historico permanente (`historico.py`) e, se esta ligado, envia o relatorio
    por e-mail (`relatorio.py`; sem RESEND_API_KEY e RELATORIO_EMAIL_PARA nao envia). A reserva do dia esta na base, por isso um arranque a meio da noite nao o duplica."""
    while True:
        extras = admin.paineis_de_outras_tabelas(servico)
        with contextlib.suppress(Exception):
            await asyncio.to_thread(historico.gravar_pendentes, servico.historico, servico.metricas, extras, ZoneInfo(config.relatorio_fuso()))
        with contextlib.suppress(Exception):
            await asyncio.to_thread(copia.fazer_se_devido, servico.relatorios, servico.estado_copia)
        with contextlib.suppress(Exception):
            await asyncio.to_thread(relatorio_periodo.enviar_periodicos_se_devido, servico.relatorios, servico.historico, servico.metricas, extras, servico.estado_relatorio)
        with contextlib.suppress(Exception):
            await asyncio.to_thread(relatorio.enviar_se_devido, servico.relatorios, servico.metricas, extras, servico.estado_relatorio,
                                    None, relatorio.urllib.request.urlopen, servico.objetivos)
        with contextlib.suppress(Exception):
            await asyncio.to_thread(indexnow.enviar_se_devido, servico.relatorios, VERSAO, config.url_publica(), servico.estado_indexnow)
        await asyncio.sleep(cada_s)


async def _vigiar(servico: Servico, cada_s: float) -> None:
    """De minuto a minuto: se algo corre mal (erros 5xx, reinicios do motor, memoria, base de dados) avisa por e-mail (`alertas.py`; mesmo destino do relatorio)."""
    while True:
        await asyncio.sleep(cada_s)
        with contextlib.suppress(Exception):
            await asyncio.to_thread(alertas.verificar_e_enviar, servico.alertas, servico.metricas, servico.estado_alertas)


SEO_LEITURA_S = 15 * 60                              # de quanto em quanto tempo se voltam a ler os textos de SEO da base


async def _atualizar_seo(servico: Servico, cada_s: float) -> None:
    """Le de 15 em 15 minutos os textos de SEO editados no painel (a 1.a vez ja no arranque). Nenhum pedido de pagina consulta a base. Uma edicao feita no painel
    aplica-se logo neste servico (`SeoBd.definir`/`repor` chamam `atualizar`): esta leitura so apanha mudancas feitas por outro processo. Ler menos vezes deixa o
    Neon gratuito adormecer entre consultas (as horas de computacao do plano gratis contam-se enquanto esta acordado)."""
    while True:
        await asyncio.to_thread(servico.seo.atualizar)
        await asyncio.sleep(cada_s)


def criar_app(frontend: Path | None = None, armazenamento: Path | None = None, motor: Motor | None = None,
              metricas: Metricas | None = None, partilhas: Partilhas | None = None, chaves: Chaves | None = None, seo_bd: SeoBd | None = None, comentarios: Comentarios | None = None) -> FastAPI:
    """`frontend`: pasta do frontend compilado; `armazenamento`: onde ficam as sessoes (RIFAS_ARMAZENAMENTO); `motor`, `metricas`: para os testes."""
    pasta = (frontend or config.pasta_frontend()).resolve()
    armazem = ArmazenamentoLocal(armazenamento, limite_bytes=config.limite_sessao_mb() * 1024 * 1024)
    servico = Servico(Sessoes(armazem), motor or Motor(tempo_maximo_s=config.tempo_maximo_geracao_min() * 60), Limitador(),
                      metricas or Metricas(caminho_por_defeito(armazem.raiz), url_bd=config.database_url(), intervalo_bd_min=config.metricas_bd_min()), Observador(armazem.raiz))

    observabilidade.configurar(config.log_pedidos())
    servico.partilhas = partilhas if partilhas is not None else (Partilhas(config.database_url()) if config.database_url() else None)
    servico.chaves = chaves if chaves is not None else Chaves(config.database_url(), armazem.raiz / "api.sqlite3")
    servico.seo = seo_bd if seo_bd is not None else SeoBd(config.database_url(), armazem.raiz / "seo.sqlite3")
    servico.comentarios = comentarios if comentarios is not None else Comentarios(config.database_url(), armazem.raiz / "comentarios.sqlite3")
    servico.alertas = alertas.AlertasEnviados(config.database_url(), armazem.raiz / "alertas.sqlite3")
    servico.auditoria = auditoria.Auditoria(config.database_url(), armazem.raiz / "auditoria.sqlite3")
    servico.objetivos = objetivos.Objetivos(config.database_url(), armazem.raiz / "objetivos.sqlite3")
    servico.historico = historico.HistoricoDiario(config.database_url(), armazem.raiz / "historico.sqlite3")
    servico.relatorios = relatorio.RelatoriosEnviados(config.database_url(), armazem.raiz / "relatorios.sqlite3")
    seo_textos.definir_sobreposicoes({})                 # cada app comeca com os textos do codigo; os editados chegam da base (`_atualizar_seo`)
    assets_rem = None
    if config.assets_zip_url() and not os.environ.get("RIFAS_ASSETS", "").strip():       # videos e capturas fora da imagem Docker (ver assets_remotos.py)
        assets_rem = AssetsRemotos(config.assets_zip_url(), config.assets_sha256(), config.pasta_assets(), ao_ficar_pronto=rotas_ajuda.esquecer_recortes)

    @contextlib.asynccontextmanager
    async def ciclo_de_vida(app: FastAPI):
        if assets_rem is not None:
            assets_rem.garantir()                            # em segundo plano: o servidor arranca (e o /health responde) sem esperar
        armazem.limpar_antigas(0)                            # pastas de um arranque anterior (nao ha sessoes em memoria para elas)
        limpeza = asyncio.create_task(_limpeza_periodica(servico, 60))
        seo_tarefa = asyncio.create_task(_atualizar_seo(servico, SEO_LEITURA_S))
        amostrador = asyncio.create_task(_amostrar(servico, 30))
        relatorio_tarefa = asyncio.create_task(_relatorio_diario(servico, 300))
        vigia = asyncio.create_task(_vigiar(servico, 60))
        url_acordado, cada_s = config.manter_acordado()
        acordado = None
        if url_acordado:
            servico.acordado.ativo, servico.acordado.url, servico.acordado.cada_s = True, url_acordado, cada_s
            acordado = asyncio.create_task(ciclo_acordado(servico.acordado))
        try:
            await servico.motor.aquecer()                    # o 1.o pedido nao paga o arranque do processo do motor
        except Exception:  # noqa: BLE001 - o servidor arranca na mesma; o motor recria-se no 1.o pedido
            servico.motor.reiniciar()
        try:
            yield
        finally:
            limpeza.cancel()
            seo_tarefa.cancel()
            amostrador.cancel()
            relatorio_tarefa.cancel()
            vigia.cancel()
            if acordado is not None:
                acordado.cancel()
            servico.motor.parar()
            with contextlib.suppress(Exception):
                servico.metricas.fechar()

    app = FastAPI(title="Gerador de Rifas", version=VERSAO, docs_url="/api/docs", redoc_url=None, openapi_url="/api/openapi.json",
                  lifespan=ciclo_de_vida)
    app.state.servico = servico
    app.state.assets = assets_rem

    @app.exception_handler(ErroApi)
    async def _erro_api(_: Request, e: ErroApi) -> JSONResponse:
        servico.metricas.evento("erro_http", str(e.estado), e.tipo)
        return JSONResponse({"detail": e.texto, "tipo": e.tipo}, status_code=e.estado)

    @app.head("/health", include_in_schema=False)
    @app.get("/health", response_model=Saude, tags=["sistema"])
    def saude() -> Saude:
        """Para o Render e para o Docker (HEALTHCHECK): 200 enquanto o servidor responde. Aceita HEAD porque os monitores externos
        (UptimeRobot, etc.) usam-no por omissão."""
        return Saude(estado="ok", versao=VERSAO)

    @app.get("/api/changelog", response_model=Changelog, tags=["sistema"])
    def changelog_api(resposta: Response, lg: str = Depends(rotas.lingua)) -> Changelog:
        """O changelog (`src/web/CHANGELOG.md`: o original, em portugues; `changelog/<lingua>.md`: um resumo traduzido) na lingua do pedido (X-Lingua)."""
        resposta.headers["Cache-Control"] = "public, max-age=300"
        resposta.headers["Vary"] = "X-Lingua, Accept-Language"        # a resposta depende da lingua: as caches nao a podem misturar
        return Changelog(entradas=[EntradaChangelog(versao=e.versao, data=e.data, seccoes=[SeccaoChangelog(titulo=s.titulo, itens=s.itens)
                                                                                           for s in e.seccoes]) for e in changelog.entradas(lg)])

    @app.get("/api/publico", response_model=Publico, tags=["sistema"])
    def publico(resposta: Response) -> Publico:
        """O que o dono configurou para o publico (variaveis de ambiente): ligacao de donativo e se ha contacto."""
        resposta.headers["Cache-Control"] = "public, max-age=300"
        return Publico(donativo_url=config.donativo_url(), contacto=bool(config.contacto_email()), qr=bool(config.verificacao_chave()),
                       anuncios_cliente=config.adsense_cliente(), anuncios_slot=config.adsense_slot(),
                       partilha_editor=servico.partilhas is not None, problemas=bool(config.github_token() and config.github_repo()))

    @app.get("/api/pagina/{nome}", response_model=PaginaTexto, tags=["sistema"])
    def pagina_de_texto(nome: str, resposta: Response, lg: str = Depends(rotas.lingua)) -> PaginaTexto:
        """Termos, privacidade e contacto (`textos_legais.py`, `legal/<lingua>.py`) na lingua do pedido (X-Lingua)."""
        if nome not in textos_legais.PAGINAS:
            raise HTTPException(404, "Página desconhecida")
        resposta.headers["Cache-Control"] = "public, max-age=300"
        resposta.headers["Vary"] = "X-Lingua, Accept-Language"        # a resposta depende da lingua: as caches nao a podem misturar
        return PaginaTexto(**textos_legais.pagina(nome, lg))

    @app.get("/api/guias", response_model=ListaGuias, tags=["sistema"])
    def lista_de_guias(resposta: Response, lg: str = Depends(rotas.lingua)) -> ListaGuias:
        """Todos os guias «como fazer» na lingua do pedido (titulo e resumo): o indice `/como-fazer` e as ligacoes entre guias."""
        resposta.headers["Cache-Control"] = "public, max-age=300"
        resposta.headers["Vary"] = "X-Lingua, Accept-Language"
        return ListaGuias(guias=[GuiaNaLista(**g) for g in guias.lista(lg)])

    @app.get("/api/guia/{nome}", response_model=GuiaTexto, tags=["sistema"])
    def guia_de_como_fazer(nome: str, resposta: Response, lg: str = Depends(rotas.lingua)) -> GuiaTexto:
        """Os guias «como fazer» (`guias/`: escolas, associacoes, clubes, bombeiros e festas) na lingua do pedido (X-Lingua)."""
        if nome not in guias.NOMES:
            raise HTTPException(404, "Guia desconhecido")
        resposta.headers["Cache-Control"] = "public, max-age=300"
        resposta.headers["Vary"] = "X-Lingua, Accept-Language"
        return GuiaTexto(**guias.guia(nome, lg))

    @app.get("/api/linguas", response_model=Linguas, tags=["textos"])
    def linguas(accept_language: str | None = Header(default=None)) -> Linguas:
        """As 18 linguas e a que corresponde ao browser (cabecalho Accept-Language)."""
        return Linguas(por_defeito=i18n.lingua_de_accept_language(accept_language),
                       linguas=[Lingua(codigo=c, nome=n) for c, n in i18n.LINGUAS.items()])

    @app.get("/api/textos/{lingua}", response_model=Textos, tags=["textos"])
    def textos(lingua: str, resposta: Response) -> Textos:
        """Todos os textos da interface numa lingua (os mesmos de `src/core/idiomas`, partilhados com a app Windows)."""
        if lingua not in i18n.LINGUAS:
            raise HTTPException(404, f"Língua desconhecida: {lingua}")
        resposta.headers["Cache-Control"] = "public, max-age=300"
        return Textos(lingua=lingua, textos={**i18n.TEXTOS["pt"], **i18n.TEXTOS[lingua]})      # o que faltar cai no portugues

    app.include_router(rotas.router)
    app.include_router(rotas_ajuda.router)
    app.include_router(rotas.router_ecra)
    app.include_router(rotas.router_desempenho)
    app.include_router(rotas_listas.router)
    app.include_router(rotas_galeria.router)
    app.include_router(rotas_precario.router)
    app.include_router(rotas_vales.router)
    app.include_router(rotas_editor.router)
    app.include_router(rotas_verificar.router)
    app.include_router(rotas_opiniao.router)
    app.include_router(admin.router)
    app.mount("/api/v1", api_v1.criar_api_v1(servico), name="api_v1")      # a API publica em lote, com o seu Swagger em /api/v1/docs

    # imagens do tutorial e videos (os mesmos ficheiros da app Windows); tem de vir antes do «fallback» do frontend
    assets = config.pasta_assets()
    for rota, sub in (("/ajuda", "ajuda"), ("/videos", "video")):
        if (assets / sub).is_dir():
            app.mount(rota, StaticFiles(directory=assets / sub), name=sub)

    @app.middleware("http")
    async def _transversal(request: Request, call_next):
        """Em toda a resposta da API: `noindex`; e mede o tempo de cada pedido da API (o painel de administracao mostra-o)."""
        t0 = time.perf_counter()
        caminho = request.url.path
        rid = observabilidade.novo_id()
        era_head = request.method == "HEAD" and not caminho.startswith(("/api/", "/health"))
        if era_head:                                                              # as paginas, o sitemap e os ficheiros respondem a HEAD como a GET, sem corpo
            request.scope["method"] = "GET"
            request.scope["rifas_head"] = True                                    # nao conta como pagina vista
        try:
            resposta = await call_next(request)
        except Exception as exc:                                                  # um erro que ninguem tratou: regista (classe e sitio, nunca a mensagem) e responde 500
            rota = getattr(request.scope.get("route"), "path", None) or "(sem rota)"
            servico.obs.excecao(rid, request.method, rota, exc)
            resposta = JSONResponse({"detail": i18n.traduzir("erro_inesperado", rotas.lingua(request), erro=rid), "tipo": "erro", "id": rid}, status_code=500)
        if era_head:
            corpo = getattr(resposta, "body_iterator", None)
            if corpo is not None and hasattr(corpo, "aclose"):
                await corpo.aclose()                                              # liberta o ficheiro/fluxo que nunca se vai ler
            resposta = RespostaSimples(b"", status_code=resposta.status_code, headers=dict(resposta.headers))      # os mesmos cabecalhos (e o mesmo Content-Length) de um GET, sem corpo
        resposta.headers["X-Request-ID"] = rid
        for nome, valor in CABECALHOS_SEGURANCA.items():
            resposta.headers.setdefault(nome, valor)
        if request.url.scheme == "https" or request.headers.get("x-forwarded-proto", "").lower() == "https":
            resposta.headers.setdefault("Strict-Transport-Security", HSTS)
        if caminho.startswith(("/api/", "/health")):
            resposta.headers["X-Robots-Tag"] = "noindex, nofollow"
        if caminho.startswith("/api/"):
            rota = getattr(request.scope.get("route"), "path", None) or "(sem rota)"
            ms = (time.perf_counter() - t0) * 1000
            servico.obs.pedido(rid, request.method, rota, resposta.status_code, ms)
            if not caminho.startswith("/api/admin"):
                servico.metricas.pedido(f"{request.method} {rota}", resposta.status_code, ms)
                servico.metricas.cliente(request.client.host if request.client else "?", bool(request.headers.get("x-forwarded-for")),
                                         "cf-ipcountry" in request.headers)
        return resposta

    @app.get("/robots.txt", include_in_schema=False)
    def robots_txt(request: Request) -> PlainTextResponse:
        return PlainTextResponse(seo.robots(seo.url_publica(request)), headers={"Cache-Control": "public, max-age=3600"})

    @app.get("/ads.txt", include_in_schema=False)
    def ads_txt() -> PlainTextResponse:
        """O `ads.txt` que a Google AdSense pede (so existe com ADSENSE_CLIENTE): quem pode vender anuncios deste site."""
        cliente = config.adsense_cliente()
        if not cliente:
            raise HTTPException(404, "Sem anúncios")
        linha = f"google.com, pub-{cliente.removeprefix('ca-pub-')}, DIRECT, f08c47fec0942fa0"
        return PlainTextResponse(linha + chr(10), headers={"Cache-Control": "public, max-age=3600"})

    base_indexnow = config.url_publica()
    if base_indexnow and indexnow.ligado(base_indexnow):
        chave_indexnow = indexnow.chave(base_indexnow)

        @app.get(f"/{chave_indexnow}.txt", include_in_schema=False)
        def indexnow_chave() -> PlainTextResponse:
            """O ficheiro público com a chave do IndexNow (prova ao Bing e aos outros que o site é nosso; não é segredo: `indexnow.py`)."""
            return PlainTextResponse(chave_indexnow, headers={"Cache-Control": "public, max-age=86400"})

    @app.get("/sitemap.xml", include_in_schema=False)
    def sitemap_xml(request: Request) -> RespostaSimples:
        return RespostaSimples(seo.sitemap(seo.url_publica(request)), media_type="application/xml", headers={"Cache-Control": "public, max-age=3600"})

    @app.get("/{caminho:path}", include_in_schema=False)
    def frontend_estatico(caminho: str, request: Request):
        """Ficheiros do frontend e as paginas da SPA. `/api...` nunca cai aqui.

        As paginas conhecidas (`seo.ROTAS`) saem com o `<head>` e o texto de SEO injetados no index.html; qualquer outra rota que nao
        seja um ficheiro e um 404 a sério (nada de «soft 404»). O `dist` traz cada ficheiro de texto ja comprimido (`.br`, `.gz`):
        entrega-se o que o browser aceita. Os mapas e as versoes comprimidas nunca se servem como ficheiros soltos."""
        if caminho == "api" or caminho.startswith("api/"):
            return JSONResponse({"detail": "Rota inexistente"}, status_code=404)
        index = pasta / "index.html"
        if not index.is_file():
            return JSONResponse({"detail": "Frontend por compilar: cd src/web/frontend && pnpm install && pnpm build"}, status_code=503)
        alvo = (pasta / caminho).resolve()
        if caminho and caminho != "index.html" and alvo.is_relative_to(pasta) and alvo.is_file():
            if alvo.suffix in _NAO_SERVIR:
                return JSONResponse({"detail": "Rota inexistente"}, status_code=404)
            cabecalhos = {"Cache-Control": "public, max-age=31536000, immutable"} if alvo.parent.name == "assets" else {}
            if alvo.name == "sw.js":                                                  # o browser tem de ver sempre a versao nova do service worker
                cabecalhos = {"Cache-Control": "no-cache"}
            return _enviar(alvo, request, cabecalhos)
        lg, sem_prefixo = seo.separar_lingua(caminho)
        if lg == "pt-prefixado":                                                    # /pt/tutorial -> /tutorial (um so URL por pagina)
            return RedirectResponse("/" + sem_prefixo.rstrip("/"), status_code=301)
        rota = "/" if sem_prefixo in ("", "index.html") else "/" + sem_prefixo.rstrip("/")
        if caminho.endswith("/") and caminho != "" and (rota in seo.ROTAS or rota in seo.SEM_INDICE):          # /tutorial/ -> /tutorial, /en/ -> /en
            return RedirectResponse(seo.caminho_na_lingua(rota, lg), status_code=301)
        base = seo.url_publica(request)
        cab = {"Cache-Control": "no-cache"}
        html_base = index.read_text(encoding="utf-8")
        if rota == "/admin" and lg == "pt":                                         # o painel: sem ADMIN_TOKEN nao existe (e so em portugues, sem prefixo)
            if not admin.ativo():
                return HTMLResponse(seo.renderizar(html_base, seo.pagina_nao_encontrada(), base), status_code=404, headers=cab)
            return HTMLResponse(seo.renderizar(html_base, seo.ADMIN, base), headers={"Cache-Control": "no-store", "X-Robots-Tag": "noindex, nofollow"})
        pagina = seo.ROTAS.get(rota) or seo.SEM_INDICE.get(rota)
        if pagina is None:
            return HTMLResponse(seo.renderizar(html_base, seo.pagina_nao_encontrada(), base), status_code=404, headers=cab)
        if not request.scope.get("rifas_head"):                                     # um HEAD (verificadores de ligacoes, pre-visualizacoes) nao e uma visita
            servico.metricas.evento("pagina", rota, c=dispositivo(request.headers.get("user-agent", "")))
        return HTMLResponse(seo.renderizar(html_base, pagina, base, lg), headers={**cab, "Content-Language": i18n.bcp47(lg)})

    return app
