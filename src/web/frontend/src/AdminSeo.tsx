import { useCallback, useEffect, useState } from "react";
import { adminApi, ErroEntrada, type ItemSeo, NaoAutenticado, type VistaSeo } from "./admin-api";

/*
 * SEO por língua editável no painel (títulos, descrições, guias «como fazer»). Guarda na base de dados do servidor; o que não for editado
 * continua a vir do código. Só em português (painel do dono). As regras (largura do título, da descrição, {parâmetros}) são as do servidor,
 * que valida ao gravar: aqui só se mostra a largura para ajudar a escrever.
 */

function largura(texto: string): number {
  let n = 0;
  for (const c of texto) {
    const p = c.codePointAt(0) ?? 0;
    n +=
      (p >= 0x1100 && p <= 0x115f) ||
      (p >= 0x2e80 && p <= 0xa4cf) ||
      (p >= 0xac00 && p <= 0xd7a3) ||
      (p >= 0xf900 && p <= 0xfaff) ||
      (p >= 0xfe30 && p <= 0xfe6f) ||
      (p >= 0xff00 && p <= 0xff60) ||
      (p >= 0xffe0 && p <= 0xffe6)
        ? 2
        : 1;
  }
  return n;
}

function Linha({
  item,
  lingua,
  vista,
  aoMudar,
  leitura,
}: {
  item: ItemSeo;
  lingua: string;
  vista: VistaSeo;
  aoMudar: () => void;
  leitura: boolean;
}) {
  const [texto, setTexto] = useState(item.valor ?? item.padrao);
  const [msg, setMsg] = useState<{ ok: boolean; texto: string } | null>(null);
  const editado = item.valor !== null;
  const limite =
    item.tipo === "descricao"
      ? vista.limites.descricao[1]
      : item.tipo === "titulo"
        ? vista.limites.titulo
        : vista.limites.max;
  const w = largura(texto);

  useEffect(() => {
    setTexto(item.valor ?? item.padrao);
    setMsg(null);
  }, [item.valor, item.padrao]);

  async function guardar() {
    try {
      const valor = await adminApi.seoGuardar(item.chave, lingua, texto);
      setTexto(valor);
      setMsg({ ok: true, texto: "Guardado." });
      aoMudar();
    } catch (e) {
      setMsg({ ok: false, texto: e instanceof ErroEntrada ? e.message : "Não foi possível guardar." });
    }
  }
  async function repor() {
    try {
      await adminApi.seoRepor(item.chave, lingua);
      setMsg({ ok: true, texto: "Reposto o texto do código." });
      aoMudar();
    } catch {
      setMsg({ ok: false, texto: "Não foi possível repor." });
    }
  }

  return (
    <li className="seo-linha" data-testid={`seo-${item.chave}`}>
      <label>
        <span className="seo-rotulo">
          {item.rotulo} {editado && <strong className="seo-editado">editado</strong>}
        </span>
        <textarea
          rows={item.tipo === "texto" ? 3 : 2}
          value={texto}
          maxLength={vista.limites.max}
          onChange={(e) => setTexto(e.target.value)}
        />
      </label>
      <p className={`explica ${w > limite ? "cor-erro" : ""}`}>
        Largura {w}
        {item.tipo !== "texto" &&
          ` / ${item.tipo === "descricao" ? `${vista.limites.descricao[0]}–${limite}` : limite}`}
      </p>
      {editado && <p className="explica">Original: {item.padrao}</p>}
      <div className="seo-botoes">
        <button
          type="button"
          onClick={() => void guardar()}
          disabled={leitura || texto.trim() === (item.valor ?? item.padrao)}
        >
          Guardar
        </button>
        {editado && (
          <button type="button" className="secundario" onClick={() => void repor()} disabled={leitura}>
            Repor o original
          </button>
        )}
        {msg && (
          <span role={msg.ok ? "status" : "alert"} className={msg.ok ? "cor-ok" : "cor-erro"}>
            {msg.texto}
          </span>
        )}
      </div>
    </li>
  );
}

export function AdminSeo({ leitura = false }: { leitura?: boolean }) {
  const [aberto, setAberto] = useState(false);
  const [lingua, setLingua] = useState("pt");
  const [vista, setVista] = useState<VistaSeo | null>(null);
  const [filtro, setFiltro] = useState("");
  const [falha, setFalha] = useState("");

  const carregar = useCallback(async () => {
    try {
      setVista(await adminApi.seoVer(lingua));
      setFalha("");
    } catch (e) {
      setFalha(
        e instanceof NaoAutenticado
          ? "A sessão expirou: recarregue a página."
          : "Não foi possível carregar os textos.",
      );
    }
  }, [lingua]);

  useEffect(() => {
    if (aberto) void carregar();
  }, [aberto, carregar]);

  const itens = (vista?.itens ?? []).filter((i) => {
    const f = filtro.trim().toLowerCase();
    return (
      !f ||
      i.rotulo.toLowerCase().includes(f) ||
      i.chave.toLowerCase().includes(f) ||
      (i.valor ?? i.padrao).toLowerCase().includes(f)
    );
  });

  return (
    <details
      className="cartao admin-seccao seo-admin"
      open={aberto}
      onToggle={(e) => setAberto(e.currentTarget.open)}
      data-testid="seo-admin"
    >
      <summary>
        <h2 id="seo">SEO por língua</h2>
      </summary>
      <p className="explica">
        Título e descrição de cada página, textos de apoio e os guias «como fazer», em cada língua. O que
        editar aqui fica na base de dados e vale em ~1 minuto, sem novo deploy; o que não editar continua a
        vir do código. As regras são as do Google: título até 66 de largura (carateres chineses, japoneses e
        coreanos contam dobro), descrição entre 50 e 158, e os mesmos {"{parâmetros}"} do original.
      </p>
      {vista && !vista.persistente && (
        <p role="note" className="cor-aviso">
          A base de dados é local e temporária (sem DATABASE_URL): estas edições perdem-se quando o serviço
          adormece ou atualiza.
        </p>
      )}
      {vista?.erro && (
        <p className="cor-aviso">A última leitura da base falhou: estão em vigor os textos de antes.</p>
      )}
      {falha && (
        <p role="alert" className="cor-erro">
          {falha}
        </p>
      )}
      <div className="seo-filtros">
        <label>
          Língua
          <select value={lingua} onChange={(e) => setLingua(e.target.value)} data-testid="seo-lingua">
            {(vista?.linguas ?? [lingua]).map((l) => (
              <option key={l} value={l}>
                {l}
              </option>
            ))}
          </select>
        </label>
        <label>
          Procurar
          <input type="search" value={filtro} onChange={(e) => setFiltro(e.target.value)} />
        </label>
      </div>
      {vista && (
        <ul className="seo-lista">
          {itens.map((i) => (
            <Linha
              key={`${lingua}|${i.chave}`}
              item={i}
              lingua={lingua}
              vista={vista}
              aoMudar={() => void carregar()}
              leitura={leitura}
            />
          ))}
        </ul>
      )}
    </details>
  );
}
