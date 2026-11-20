import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api, ErroApi, type PedidoPrecario, type PrecarioCatalogo } from "./api";
import { useDialogos } from "./dialogos";
import { guardarBlob } from "./Gerador";
import { useI18n } from "./i18n";
import { Voltar } from "./paginas";
import { Vales } from "./Vales";

/** Uma linha do preçário: um artigo do catálogo (`artigo`) ou um texto livre (`nome`); `preco` é o que a pessoa escreveu. */
interface Linha {
  chave: string;
  artigo: string;
  nome: string;
  categoria: string;
  emoji: string;
  preco: string;
}

interface Estado {
  ocasiao: string;
  desenho: string;
  linhas: Linha[];
  titulo: string;
  subtitulo: string;
  rodape: string;
  pais: string;
  moeda: string;
  inventada: boolean;
  invNome: string;
  invAntes: boolean;
  invCasas: number;
  formato: string;
  orientacao: string;
  colunas: number;
  imagens: boolean;
}

const CHAVE = "rifas.precario";
const ATRASO_MS = 450;

const semAcentos = (s: string) => s.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();

/** O país da região do idioma do browser (`en-GB` → GB) se for um que conhecemos; senão o que o servidor sugere para a língua. Nada vai ao servidor. */
export function paisDoBrowser(paises: Record<string, string>, padrao: string): string {
  try {
    const r = new Intl.Locale(navigator.language).region;
    if (r && paises[r]) return r;
  } catch {
    /* sem Intl.Locale */
  }
  return padrao;
}

function nomeDoPais(codigo: string, lingua: string): string {
  try {
    return new Intl.DisplayNames([lingua], { type: "region" }).of(codigo) ?? codigo;
  } catch {
    return codigo;
  }
}

/** O estado de partida: o rascunho do browser se existir e servir, senão a ocasião sugerida para o mês (ou a festa popular). */
export function estadoInicial(cat: PrecarioCatalogo, mes: number, guardado: unknown): Estado {
  const ids = new Set(cat.categorias.flatMap((c) => c.artigos.map((a) => a.id)));
  const g = (guardado ?? {}) as Partial<Estado>;
  if (g && Array.isArray(g.linhas) && g.linhas.length > 0 && typeof g.titulo === "string") {
    const linhas = g.linhas.filter(
      (l): l is Linha =>
        !!l &&
        typeof l.chave === "string" &&
        typeof l.preco === "string" &&
        typeof l.nome === "string" &&
        (!l.artigo || ids.has(l.artigo)),
    );
    if (linhas.length > 0) return { ...base(cat, mes), ...g, linhas } as Estado;
  }
  return base(cat, mes);
}

function base(cat: PrecarioCatalogo, mes: number): Estado {
  const oc =
    cat.ocasioes.find((o) => o.id === cat.sugerida) ??
    cat.ocasioes.find((o) => o.meses.includes(mes)) ??
    cat.ocasioes[0];
  const nome = oc?.nome ?? "";
  return {
    ocasiao: oc?.id ?? "",
    desenho: oc?.desenho ?? "quermesse",
    linhas: (oc?.artigos ?? []).map((a) => ({
      chave: a,
      artigo: a,
      nome: "",
      categoria: "",
      emoji: "",
      preco: "",
    })),
    titulo: nome.slice(0, cat.limites.titulo),
    subtitulo: "",
    rodape: "",
    pais: paisDoBrowser(cat.paises, cat.pais),
    moeda: cat.paises[paisDoBrowser(cat.paises, cat.pais)] ?? cat.moeda,
    inventada: false,
    invNome: "",
    invAntes: false,
    invCasas: 0,
    formato: "A4",
    orientacao: "vertical",
    colunas: 0,
    imagens: true,
  };
}

export function pedidoDoEstado(e: Estado): PedidoPrecario {
  return {
    linhas: e.linhas.map((l) => ({
      artigo: l.artigo,
      nome: l.artigo ? "" : l.nome,
      preco: l.preco.trim(),
      categoria: l.artigo ? "" : l.categoria,
      emoji: l.artigo ? "" : l.emoji,
    })),
    titulo: e.titulo.trim(),
    subtitulo: e.subtitulo.trim(),
    rodape: e.rodape.trim(),
    desenho: e.desenho,
    formato: e.formato,
    orientacao: e.orientacao,
    colunas: e.colunas,
    imagens: e.imagens,
    moeda:
      e.inventada && e.invNome.trim()
        ? { nome: e.invNome.trim(), antes: e.invAntes, decimais: e.invCasas }
        : { codigo: e.moeda },
  };
}

function Miniatura({ emoji }: { emoji: string }) {
  if (!emoji) return <span className="precario-sem-imagem" aria-hidden="true" />;
  return (
    <img src={`/precario/${emoji}.webp`} alt="" width={28} height={28} loading="lazy" decoding="async" />
  );
}

/**
 * O gerador de preçários: escolhe-se a ocasião (e o tema), os artigos, os preços (na moeda do país ou numa inventada) e o aspeto; a pré-visualização
 * desenha-se no servidor a cada alteração e o PDF (ou a imagem) descarrega-se. Nada se guarda no servidor; o rascunho fica só neste browser.
 */
export function Precario() {
  const { t, lingua } = useI18n();
  const { aviso } = useDialogos();
  const mes = useMemo(() => new Date().getMonth() + 1, []);
  const [cat, setCat] = useState<PrecarioCatalogo | null>(null);
  const [e, setE] = useState<Estado | null>(null);
  const [pesquisa, setPesquisa] = useState("");
  const [meu, setMeu] = useState("");
  const [previa, setPrevia] = useState("");
  const [erro, setErro] = useState("");
  const [aDesenhar, setADesenhar] = useState(false);
  const contador = useRef(0);

  // o catálogo na língua do site (muda quando a língua muda)
  // biome-ignore lint/correctness/useExhaustiveDependencies: o catálogo pede-se de novo quando a língua muda
  useEffect(() => {
    let ativo = true;
    api
      .precarioCatalogo(mes)
      .then((c) => {
        if (!ativo) return;
        setCat(c);
        let guardado: unknown = null;
        try {
          guardado = JSON.parse(localStorage.getItem(CHAVE) ?? "null");
        } catch {
          /* sem armazenamento ou rascunho estragado */
        }
        setE((antes) => {
          if (!antes) return estadoInicial(c, mes, guardado);
          const ids = new Set(c.categorias.flatMap((x) => x.artigos.map((a) => a.id)));
          return { ...antes, linhas: antes.linhas.filter((l) => !l.artigo || ids.has(l.artigo)) }; // um artigo de uma região que a língua nova não vê sai
        });
      })
      .catch((x: unknown) => ativo && setErro(x instanceof ErroApi ? x.message : String(x)));
    return () => {
      ativo = false;
    };
  }, [lingua, mes]);

  const artigos = useMemo(() => {
    const m = new Map<string, { nome: string; emoji: string; categoria: string }>();
    for (const c of cat?.categorias ?? [])
      for (const a of c.artigos) m.set(a.id, { nome: a.nome, emoji: a.emoji, categoria: c.id });
    return m;
  }, [cat]);

  const pedido = useMemo(() => (e ? pedidoDoEstado(e) : null), [e]);
  const chavePedido = pedido ? JSON.stringify(pedido) : "";

  // o rascunho: só neste browser
  useEffect(() => {
    if (!e) return;
    try {
      localStorage.setItem(CHAVE, JSON.stringify(e));
    } catch {
      /* sem armazenamento */
    }
  }, [e]);

  // a pré-visualização (desenhada no servidor, sem guardar nada), com um pequeno atraso para não pedir a cada tecla
  // biome-ignore lint/correctness/useExhaustiveDependencies: `chavePedido` resume o pedido inteiro
  useEffect(() => {
    if (!pedido || pedido.linhas.length === 0) {
      setPrevia("");
      setErro("");
      return;
    }
    const ctl = new AbortController();
    const eu = ++contador.current;
    const espera = setTimeout(() => {
      setADesenhar(true);
      api
        .precarioPrevia(pedido, ctl.signal)
        .then((b) => {
          if (eu !== contador.current) return;
          setPrevia((antes) => {
            if (antes) URL.revokeObjectURL(antes);
            return URL.createObjectURL(b);
          });
          setErro("");
        })
        .catch((x: unknown) => {
          if (x instanceof DOMException && x.name === "AbortError") return;
          if (eu === contador.current) setErro(x instanceof ErroApi ? x.message : String(x));
        })
        .finally(() => eu === contador.current && setADesenhar(false));
    }, ATRASO_MS);
    return () => {
      clearTimeout(espera);
      ctl.abort();
    };
  }, [chavePedido, lingua]);

  const mudar = useCallback(
    (campos: Partial<Estado>) => setE((antes) => (antes ? { ...antes, ...campos } : antes)),
    [],
  );

  if (!cat || !e)
    return <div className="pagina">{erro ? <p role="alert">{erro}</p> : <p aria-busy="true">…</p>}</div>;

  const ocasiaoAtual = (id: string) => {
    const o = cat.ocasioes.find((x) => x.id === id);
    if (!o) return;
    const anteriores = new Map(e.linhas.map((l) => [l.artigo || l.chave, l.preco]));
    const nomeAntigo = cat.ocasioes.find((x) => x.id === e.ocasiao)?.nome ?? "";
    mudar({
      ocasiao: id,
      desenho: o.desenho,
      linhas: [
        ...o.artigos.map((a) => ({
          chave: a,
          artigo: a,
          nome: "",
          categoria: "",
          emoji: "",
          preco: anteriores.get(a) ?? "",
        })),
        ...e.linhas.filter((l) => !l.artigo),
      ],
      titulo: !e.titulo.trim() || e.titulo === nomeAntigo ? o.nome.slice(0, cat.limites.titulo) : e.titulo,
    });
  };
  const alternar = (id: string) => {
    const ja = e.linhas.some((l) => l.artigo === id);
    mudar({
      linhas: ja
        ? e.linhas.filter((l) => l.artigo !== id)
        : [...e.linhas, { chave: id, artigo: id, nome: "", categoria: "", emoji: "", preco: "" }],
    });
  };
  const juntar = () => {
    const nome = meu.trim().slice(0, cat.limites.nome);
    if (!nome || e.linhas.length >= cat.limites.linhas) return;
    mudar({
      linhas: [
        ...e.linhas,
        { chave: `c${Date.now()}`, artigo: "", nome, categoria: "extras", emoji: "", preco: "" },
      ],
    });
    setMeu("");
  };
  const mudarPreco = (chave: string, preco: string) =>
    mudar({ linhas: e.linhas.map((l) => (l.chave === chave ? { ...l, preco } : l)) });
  const precoDaCategoria = (id: string, preco: string) =>
    mudar({
      linhas: e.linhas.map((l) =>
        (l.artigo ? artigos.get(l.artigo)?.categoria : l.categoria) === id ? { ...l, preco } : l,
      ),
    });
  const nomeDe = (l: Linha) => l.nome || artigos.get(l.artigo)?.nome || l.artigo;
  const emojiDe = (l: Linha) => l.emoji || artigos.get(l.artigo)?.emoji || "";
  const categoriaDe = (l: Linha) => (l.artigo ? artigos.get(l.artigo)?.categoria : l.categoria) || "extras";
  const filtro = semAcentos(pesquisa.trim());
  const sugerida = cat.ocasioes.find((o) => o.id === cat.sugerida);
  const moedaAtual = cat.moedas.find((m) => m.codigo === e.moeda);

  const descarregar = async (fazer: (p: PedidoPrecario) => Promise<Blob>, nome: string) => {
    if (!pedido) return;
    try {
      guardarBlob(await fazer(pedido), nome);
    } catch (x) {
      aviso(x instanceof ErroApi ? x.message : String(x));
    }
  };

  return (
    <div className="pagina precario">
      <article className="cartao texto-pagina" data-testid="precario">
        <h1>{t("web_precario_titulo")}</h1>
        <p className="texto-longo">{t("web_precario_intro")}</p>
        <p>
          <Voltar />
        </p>
      </article>
      <div className="precario-grelha">
        <div className="precario-editor">
          <section className="cartao texto-pagina">
            <h2>{t("web_precario_ocasiao")}</h2>
            <label>
              <span className="so-leitores">{t("web_precario_ocasiao")}</span>
              <select
                data-testid="precario-ocasiao"
                value={e.ocasiao}
                onChange={(ev) => ocasiaoAtual(ev.target.value)}
              >
                {cat.ocasioes.map((o) => (
                  <option key={o.id} value={o.id}>
                    {o.id === cat.sugerida ? `★ ${o.nome}` : o.nome}
                  </option>
                ))}
              </select>
            </label>
            {sugerida && sugerida.id !== e.ocasiao && (
              <p>
                <button
                  type="button"
                  className="botao secundario"
                  data-testid="precario-sugerida"
                  onClick={() => ocasiaoAtual(sugerida.id)}
                >
                  {t("web_precario_sugerida")}: {sugerida.nome}
                </button>
              </p>
            )}
            <label>
              {t("web_precario_aspeto")}
              <select
                data-testid="precario-desenho"
                value={e.desenho}
                onChange={(ev) => mudar({ desenho: ev.target.value })}
              >
                {cat.desenhos.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.nome}
                  </option>
                ))}
              </select>
            </label>
          </section>

          <section className="cartao texto-pagina">
            <h2>{t("web_precario_artigos")}</h2>
            <input
              type="search"
              data-testid="precario-pesquisa"
              placeholder={t("web_precario_pesquisar")}
              aria-label={t("web_precario_pesquisar")}
              value={pesquisa}
              onChange={(ev) => setPesquisa(ev.target.value)}
            />
            {cat.categorias.map((c) => {
              const lista = c.artigos.filter((a) => !filtro || semAcentos(a.nome).includes(filtro));
              if (lista.length === 0) return null;
              return (
                <fieldset key={c.id} className="precario-categoria">
                  <legend>{c.nome}</legend>
                  <div className="precario-fichas">
                    {lista.map((a) => {
                      const ligado = e.linhas.some((l) => l.artigo === a.id);
                      return (
                        <button
                          key={a.id}
                          type="button"
                          className={`precario-ficha${ligado ? " ligada" : ""}`}
                          aria-pressed={ligado}
                          data-testid={`precario-artigo-${a.id}`}
                          onClick={() => alternar(a.id)}
                        >
                          <Miniatura emoji={a.emoji} />
                          <span>{a.nome}</span>
                        </button>
                      );
                    })}
                  </div>
                </fieldset>
              );
            })}
            <div className="precario-meu">
              <input
                data-testid="precario-meu-nome"
                placeholder={t("web_precario_nome_artigo")}
                aria-label={t("web_precario_nome_artigo")}
                maxLength={cat.limites.nome}
                value={meu}
                onChange={(ev) => setMeu(ev.target.value)}
                onKeyDown={(ev) => ev.key === "Enter" && juntar()}
              />
              <button
                type="button"
                className="botao secundario"
                data-testid="precario-meu-juntar"
                onClick={juntar}
                disabled={!meu.trim()}
              >
                {t("web_precario_meu_artigo")}
              </button>
            </div>
          </section>

          <section className="cartao texto-pagina">
            <h2>{t("web_precario_escolhidos", { n: e.linhas.length })}</h2>
            <p className="suave">{t("web_precario_dica_preco")}</p>
            {cat.categorias.map((c) => {
              const dela = e.linhas.filter((l) => categoriaDe(l) === c.id);
              if (dela.length === 0) return null;
              return (
                <fieldset key={c.id} className="precario-categoria">
                  <legend>{c.nome}</legend>
                  <label className="precario-linha precario-linha-categoria">
                    <span>{t("web_precario_preco_categoria")}</span>
                    <input
                      inputMode="decimal"
                      data-testid={`precario-preco-categoria-${c.id}`}
                      placeholder={t("web_precario_preco")}
                      maxLength={24}
                      onChange={(ev) => precoDaCategoria(c.id, ev.target.value)}
                    />
                  </label>
                  {dela.map((l) => (
                    <div className="precario-linha" key={l.chave}>
                      <Miniatura emoji={emojiDe(l)} />
                      <span className="precario-nome">{nomeDe(l)}</span>
                      <input
                        inputMode="decimal"
                        data-testid={`precario-preco-${l.chave}`}
                        aria-label={`${t("web_precario_preco")}: ${nomeDe(l)}`}
                        placeholder={t("web_precario_preco")}
                        maxLength={24}
                        value={l.preco}
                        onChange={(ev) => mudarPreco(l.chave, ev.target.value)}
                      />
                      <button
                        type="button"
                        className="botao secundario"
                        aria-label={`${t("web_precario_tirar")}: ${nomeDe(l)}`}
                        onClick={() => mudar({ linhas: e.linhas.filter((x) => x.chave !== l.chave) })}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </fieldset>
              );
            })}
          </section>

          <section className="cartao texto-pagina">
            <h2>{t("web_precario_moeda")}</h2>
            <label>
              {t("web_precario_pais")}
              <select
                data-testid="precario-pais"
                value={e.pais}
                onChange={(ev) =>
                  mudar({ pais: ev.target.value, moeda: cat.paises[ev.target.value] ?? e.moeda })
                }
              >
                {Object.keys(cat.paises)
                  .sort((a, b) => nomeDoPais(a, lingua).localeCompare(nomeDoPais(b, lingua), lingua))
                  .map((p) => (
                    <option key={p} value={p}>
                      {nomeDoPais(p, lingua)}
                    </option>
                  ))}
              </select>
            </label>
            <label>
              {t("web_precario_moeda")}
              <select
                data-testid="precario-moeda"
                value={e.moeda}
                onChange={(ev) => mudar({ moeda: ev.target.value })}
                disabled={e.inventada}
              >
                {cat.moedas.map((m) => (
                  <option key={m.codigo} value={m.codigo}>
                    {m.codigo} ({m.simbolo})
                  </option>
                ))}
              </select>
            </label>
            <label className="precario-caixa">
              <input
                type="checkbox"
                data-testid="precario-inventada"
                checked={e.inventada}
                onChange={(ev) => mudar({ inventada: ev.target.checked })}
              />
              {t("web_precario_moeda_inventada")}
            </label>
            {e.inventada && (
              <div className="precario-inventada">
                <label>
                  {t("web_precario_inventada_nome")}
                  <input
                    data-testid="precario-inv-nome"
                    maxLength={cat.limites.moeda_inventada}
                    value={e.invNome}
                    onChange={(ev) => mudar({ invNome: ev.target.value })}
                  />
                </label>
                <label className="precario-caixa">
                  <input
                    type="checkbox"
                    checked={e.invAntes}
                    onChange={(ev) => mudar({ invAntes: ev.target.checked })}
                  />
                  {t("web_precario_inventada_antes")}
                </label>
                <label>
                  {t("web_precario_inventada_casas")}
                  <select value={e.invCasas} onChange={(ev) => mudar({ invCasas: Number(ev.target.value) })}>
                    {[0, 1, 2].map((n) => (
                      <option key={n} value={n}>
                        {n}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            )}
            {moedaAtual && !e.inventada && (
              <p className="suave">{`${nomeDoPais(e.pais, lingua)} · ${moedaAtual.codigo} ${moedaAtual.simbolo}`}</p>
            )}
          </section>

          {e.inventada && e.invNome.trim() && (
            <Vales desenho={e.desenho} moeda={e.invNome.trim()} organizacao={e.subtitulo} />
          )}

          <section className="cartao texto-pagina">
            <h2>{t("web_precario_aspeto")}</h2>
            <label>
              {t("web_precario_campo_titulo")}
              <input
                data-testid="precario-titulo"
                maxLength={cat.limites.titulo}
                value={e.titulo}
                onChange={(ev) => mudar({ titulo: ev.target.value })}
              />
            </label>
            <label>
              {t("web_precario_campo_subtitulo")}
              <input
                data-testid="precario-subtitulo"
                maxLength={cat.limites.subtitulo}
                value={e.subtitulo}
                onChange={(ev) => mudar({ subtitulo: ev.target.value })}
              />
            </label>
            <label>
              {t("web_precario_campo_rodape")}
              <input
                data-testid="precario-rodape"
                maxLength={cat.limites.rodape}
                value={e.rodape}
                onChange={(ev) => mudar({ rodape: ev.target.value })}
              />
            </label>
            <div className="precario-opcoes">
              <label>
                {t("web_precario_formato")}
                <select
                  data-testid="precario-formato"
                  value={e.formato}
                  onChange={(ev) => mudar({ formato: ev.target.value })}
                >
                  {cat.formatos.map((f) => (
                    <option key={f} value={f}>
                      {f}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                {t("web_precario_vertical")} / {t("web_precario_horizontal")}
                <select
                  data-testid="precario-orientacao"
                  value={e.orientacao}
                  onChange={(ev) => mudar({ orientacao: ev.target.value })}
                >
                  <option value="vertical">{t("web_precario_vertical")}</option>
                  <option value="horizontal">{t("web_precario_horizontal")}</option>
                </select>
              </label>
              <label>
                {t("web_precario_colunas")}
                <select
                  data-testid="precario-colunas"
                  value={e.colunas}
                  onChange={(ev) => mudar({ colunas: Number(ev.target.value) })}
                >
                  <option value={0}>{t("web_precario_auto")}</option>
                  {[1, 2, 3].map((n) => (
                    <option key={n} value={n}>
                      {n}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <label className="precario-caixa">
              <input
                type="checkbox"
                data-testid="precario-imagens"
                checked={e.imagens}
                onChange={(ev) => mudar({ imagens: ev.target.checked })}
              />
              {t("web_precario_imagens")}
            </label>
          </section>
        </div>

        <aside className="precario-previa cartao texto-pagina" aria-live="polite">
          <h2>{t("web_precario_previa")}</h2>
          {e.linhas.length === 0 ? (
            <p data-testid="precario-vazio">{t("web_precario_vazio")}</p>
          ) : previa ? (
            <img
              className={`precario-imagem${aDesenhar ? " a-desenhar" : ""}`}
              src={previa}
              alt={t("web_precario_previa")}
              data-testid="precario-previa-img"
            />
          ) : (
            <p aria-busy="true">{t("web_precario_a_desenhar")}</p>
          )}
          {erro && (
            <p role="alert" data-testid="precario-erro">
              {erro}
            </p>
          )}
          <div className="precario-acoes">
            <button
              type="button"
              className="botao"
              data-testid="precario-pdf"
              disabled={e.linhas.length === 0}
              onClick={() => void descarregar(api.precarioPdf, "precario.pdf")}
            >
              {t("web_precario_pdf")}
            </button>
            <button
              type="button"
              className="botao secundario"
              data-testid="precario-imagem"
              disabled={e.linhas.length === 0}
              onClick={() => void descarregar(api.precarioImagem, "precario.png")}
            >
              {t("web_precario_imagem")}
            </button>
            <button
              type="button"
              className="botao secundario"
              data-testid="precario-recomecar"
              onClick={() => {
                try {
                  localStorage.removeItem(CHAVE);
                } catch {
                  /* sem armazenamento */
                }
                setE(base(cat, mes));
                setPesquisa("");
              }}
            >
              {t("web_precario_recomecar")}
            </button>
          </div>
        </aside>
      </div>
    </div>
  );
}
