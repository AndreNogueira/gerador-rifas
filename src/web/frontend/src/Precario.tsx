import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api, ErroApi, type PedidoPrecario, type PrecarioCatalogo } from "./api";
import { useDialogos } from "./dialogos";
import { prepararFoto } from "./foto";
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
  /** O segundo preço (só com «dois tamanhos»); os rascunhos antigos não o têm. */
  preco2?: string;
  /** A foto própria (`data:image/…`, já reduzida): só vive nesta página (nem no rascunho nem na ligação partilhada). */
  foto?: string;
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
  /** Dois preços por artigo e os nomes das duas colunas (vazios = os da língua). */
  tamanhos: boolean;
  rotulo1: string;
  rotulo2: string;
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

/** Os milésimos de um preço como o texto que se escreve na língua (sem milhares): 1500 → «1,5» em português. */
function textoDoPreco(milesimos: unknown, lingua: string): string {
  if (typeof milesimos !== "number" || !Number.isFinite(milesimos)) return "";
  return (milesimos / 1000).toLocaleString(lingua, { useGrouping: false, maximumFractionDigits: 3 });
}

/** O estado de um preçário partilhado (`para_dict` do servidor); `null` se não se reconhece. Só se aproveita o que a página conhece. */
export function estadoDePartilha(
  cat: PrecarioCatalogo,
  antes: Estado,
  d: unknown,
  lingua: string,
): Estado | null {
  const p = d as Record<string, unknown> | null;
  if (!p || typeof p !== "object" || !Array.isArray(p.linhas) || p.linhas.length === 0) return null;
  const ids = new Set(cat.categorias.flatMap((c) => c.artigos.map((a) => a.id)));
  const texto = (v: unknown) => (typeof v === "string" ? v : "");
  const linhas: Linha[] = [];
  p.linhas.forEach((x: unknown, i: number) => {
    const l = (x ?? {}) as Record<string, unknown>;
    const artigo = texto(l.artigo);
    if (artigo && !ids.has(artigo)) return;
    linhas.push({
      chave: artigo || `c${i}`,
      artigo,
      nome: texto(l.nome),
      categoria: texto(l.categoria),
      emoji: texto(l.emoji),
      preco: textoDoPreco(l.preco, lingua),
      preco2: textoDoPreco(l.preco2, lingua),
    });
  });
  if (linhas.length === 0) return null;
  const m = (p.moeda ?? {}) as Record<string, unknown>;
  const inventada = texto(m.nome).trim() !== "";
  const codigo = texto(m.codigo);
  const pais =
    !inventada && codigo
      ? cat.paises[antes.pais] === codigo
        ? antes.pais
        : (Object.keys(cat.paises).find((k) => cat.paises[k] === codigo) ?? antes.pais)
      : antes.pais;
  const rotulos = Array.isArray(p.rotulos) ? p.rotulos : [];
  return {
    ...antes,
    ocasiao: "",
    desenho: texto(p.desenho) || antes.desenho,
    linhas,
    titulo: texto(p.titulo),
    subtitulo: texto(p.subtitulo),
    rodape: texto(p.rodape),
    pais,
    moeda: !inventada && codigo ? codigo : (cat.paises[pais] ?? antes.moeda),
    inventada,
    invNome: inventada ? texto(m.nome) : "",
    invAntes: m.antes === true,
    invCasas: typeof m.decimais === "number" ? m.decimais : 0,
    formato: texto(p.formato) || "A4",
    orientacao: texto(p.orientacao) || "vertical",
    colunas: typeof p.colunas === "number" ? p.colunas : 0,
    imagens: p.imagens !== false,
    tamanhos: p.tamanhos === true,
    rotulo1: texto(rotulos[0]),
    rotulo2: texto(rotulos[1]),
  };
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
    tamanhos: false,
    rotulo1: "",
    rotulo2: "",
  };
}

export function pedidoDoEstado(e: Estado, padroes: [string, string] = ["P", "G"]): PedidoPrecario {
  return {
    linhas: e.linhas.map((l) => ({
      artigo: l.artigo,
      nome: l.artigo ? "" : l.nome,
      preco: l.preco.trim(),
      preco2: e.tamanhos ? (l.preco2 ?? "").trim() : "",
      ...(l.foto ? { foto: l.foto } : {}),
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
    tamanhos: e.tamanhos,
    rotulos: [e.rotulo1.trim() || padroes[0], e.rotulo2.trim() || padroes[1]],
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
export function Precario({ partilha = false }: { partilha?: boolean }) {
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
  const [ligacao, setLigacao] = useState("");
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
          if (!antes) {
            const inicial = estadoInicial(c, mes, guardado);
            return inicial;
          }
          const ids = new Set(c.categorias.flatMap((x) => x.artigos.map((a) => a.id)));
          return { ...antes, linhas: antes.linhas.filter((l) => !l.artigo || ids.has(l.artigo)) }; // um artigo de uma região que a língua nova não vê sai
        });
      })
      .catch((x: unknown) => ativo && setErro(x instanceof ErroApi ? x.message : String(x)));
    return () => {
      ativo = false;
    };
  }, [lingua, mes]);

  // abrir uma ligação partilhada (`/precario?p=<id>`): só uma vez, quando o catálogo já chegou; depois a ligação sai do endereço
  const idPartilha = useRef(new URLSearchParams(window.location.search).get("p"));
  // biome-ignore lint/correctness/useExhaustiveDependencies: só depois de o catálogo chegar
  useEffect(() => {
    const id = idPartilha.current;
    if (!id || !cat || !e) return;
    idPartilha.current = null;
    api
      .precarioPartilhado(id)
      .then((r) => {
        const aberto = estadoDePartilha(cat, e, r.precario, lingua);
        if (aberto) setE(aberto);
        else setErro(t("web_precario_ligacao_invalida"));
        window.history.replaceState({}, "", window.location.pathname);
      })
      .catch((x: unknown) => setErro(x instanceof ErroApi ? x.message : t("web_precario_ligacao_invalida")));
  }, [cat, e]);

  const artigos = useMemo(() => {
    const m = new Map<string, { nome: string; emoji: string; categoria: string }>();
    for (const c of cat?.categorias ?? [])
      for (const a of c.artigos) m.set(a.id, { nome: a.nome, emoji: a.emoji, categoria: c.id });
    return m;
  }, [cat]);

  const padroes = useMemo<[string, string]>(
    () => [t("web_precario_tamanho_1"), t("web_precario_tamanho_2")],
    [t],
  );
  const pedido = useMemo(() => (e ? pedidoDoEstado(e, padroes) : null), [e, padroes]);
  const chavePedido = pedido ? JSON.stringify(pedido) : "";

  // o rascunho: só neste browser
  useEffect(() => {
    if (!e) return;
    try {
      localStorage.setItem(
        CHAVE,
        JSON.stringify({ ...e, linhas: e.linhas.map(({ foto: _foto, ...resto }) => resto) }), // as fotos não ficam no rascunho
      );
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
  const mudarFoto = (chave: string, foto: string) =>
    mudar({ linhas: e.linhas.map((l) => (l.chave === chave ? { ...l, foto } : l)) });
  const escolherFoto = async (chave: string, ficheiro: File | undefined) => {
    if (!ficheiro) return;
    try {
      mudarFoto(chave, await prepararFoto(ficheiro));
    } catch {
      aviso(t("err_editor_imagem"));
    }
  };
  const mudarPreco2 = (chave: string, preco2: string) =>
    mudar({ linhas: e.linhas.map((l) => (l.chave === chave ? { ...l, preco2 } : l)) });
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

  const partilharLigacao = async () => {
    if (!pedido) return;
    try {
      const r = await api.partilharPrecario(pedido);
      const url = `${window.location.origin}/precario?p=${r.id}`;
      setLigacao(url);
      setErro("");
      await navigator.clipboard?.writeText(url).catch(() => undefined);
    } catch (x) {
      setErro(x instanceof ErroApi ? x.message : t("web_precario_ligacao_invalida"));
    }
  };

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
            <p className="suave">{t("web_precario_fotos_dica")}</p>
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
                      {l.foto ? (
                        <button
                          type="button"
                          className="precario-foto"
                          data-testid={`precario-foto-tirar-${l.chave}`}
                          title={t("web_precario_foto_tirar")}
                          aria-label={`${t("web_precario_foto_tirar")}: ${nomeDe(l)}`}
                          onClick={() => mudarFoto(l.chave, "")}
                        >
                          <img src={l.foto} alt="" />
                        </button>
                      ) : (
                        <label className="precario-foto botao secundario" title={t("web_precario_foto")}>
                          {t("web_precario_foto")}
                          <input
                            type="file"
                            accept="image/png,image/jpeg"
                            hidden
                            data-testid={`precario-foto-${l.chave}`}
                            aria-label={`${t("web_precario_foto")}: ${nomeDe(l)}`}
                            onChange={(ev) => {
                              void escolherFoto(l.chave, ev.target.files?.[0]);
                              ev.target.value = "";
                            }}
                          />
                        </label>
                      )}
                      <input
                        inputMode="decimal"
                        data-testid={`precario-preco-${l.chave}`}
                        aria-label={`${t("web_precario_preco")}: ${nomeDe(l)}`}
                        placeholder={t("web_precario_preco")}
                        maxLength={24}
                        value={l.preco}
                        onChange={(ev) => mudarPreco(l.chave, ev.target.value)}
                      />
                      {e.tamanhos && (
                        <input
                          inputMode="decimal"
                          data-testid={`precario-preco2-${l.chave}`}
                          aria-label={`${e.rotulo2.trim() || padroes[1]}: ${nomeDe(l)}`}
                          placeholder={e.rotulo2.trim() || padroes[1]}
                          maxLength={24}
                          value={l.preco2 ?? ""}
                          onChange={(ev) => mudarPreco2(l.chave, ev.target.value)}
                        />
                      )}
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
                      {f === "A6x4" ? t("web_precario_cartoes") : f}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                {t("web_precario_vertical")} / {t("web_precario_horizontal")}
                <select
                  data-testid="precario-orientacao"
                  disabled={e.formato === "A6x4"}
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
            <label className="precario-caixa">
              <input
                type="checkbox"
                data-testid="precario-tamanhos"
                checked={e.tamanhos}
                onChange={(ev) => mudar({ tamanhos: ev.target.checked })}
              />
              {t("web_precario_tamanhos")}
            </label>
            {e.tamanhos && (
              <fieldset className="precario-rotulos">
                <legend>{t("web_precario_rotulos")}</legend>
                <input
                  data-testid="precario-rotulo-1"
                  aria-label={`${t("web_precario_rotulos")} 1`}
                  placeholder={padroes[0]}
                  maxLength={10}
                  value={e.rotulo1}
                  onChange={(ev) => mudar({ rotulo1: ev.target.value })}
                />
                <input
                  data-testid="precario-rotulo-2"
                  aria-label={`${t("web_precario_rotulos")} 2`}
                  placeholder={padroes[1]}
                  maxLength={10}
                  value={e.rotulo2}
                  onChange={(ev) => mudar({ rotulo2: ev.target.value })}
                />
              </fieldset>
            )}
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
          {ligacao && (
            <p role="status" data-testid="precario-ligacao">
              {t("web_precario_partilha_ok")} <code>{ligacao}</code>
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
            {partilha && (
              <button
                type="button"
                className="botao secundario"
                data-testid="precario-partilhar"
                disabled={e.linhas.length === 0}
                onClick={() => void partilharLigacao()}
              >
                {t("web_editor_partilhar")}
              </button>
            )}
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
