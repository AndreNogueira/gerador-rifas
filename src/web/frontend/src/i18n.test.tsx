import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ProvedorI18n, traduzir, useI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

describe("traduzir", () => {
  const textos = { ola: "Olá {nome}, tem {n} novas", simples: "sem parâmetros" };

  it("troca os parâmetros", () => {
    expect(traduzir(textos, "ola", { nome: "Ana", n: 3 })).toBe("Olá Ana, tem 3 novas");
  });
  it("deixa o que não foi dado, como o str.format do motor", () => {
    expect(traduzir(textos, "ola", { nome: "Ana" })).toBe("Olá Ana, tem {n} novas");
  });
  it("sem parâmetros devolve o texto tal e qual", () => {
    expect(traduzir(textos, "ola")).toBe("Olá {nome}, tem {n} novas");
    expect(traduzir(textos, "simples")).toBe("sem parâmetros");
  });
  it("chave desconhecida devolve a própria chave", () => {
    expect(traduzir(textos, "nao_existe")).toBe("nao_existe");
  });
});

function Amostra() {
  const { t, lingua, linguas, mudarLingua } = useI18n();
  return (
    <>
      <h1>{t("app_nome")}</h1>
      <select value={lingua} onChange={(e) => mudarLingua(e.target.value)} aria-label="lingua">
        {linguas.map((l) => (
          <option key={l.codigo} value={l.codigo}>
            {l.nome}
          </option>
        ))}
      </select>
    </>
  );
}

describe("ProvedorI18n", () => {
  beforeEach(() => {
    localStorage.clear();
    new ServidorFalso().instalar();
  });
  afterEach(() => vi.unstubAllGlobals());

  it("sem prefixo no URL mostra sempre português e muda de língua ao escolher no seletor", async () => {
    render(
      <ProvedorI18n>
        <Amostra />
      </ProvedorI18n>,
    );
    expect(await screen.findByRole("heading", { name: "Gerador de Rifas" })).toBeInTheDocument();
    await userEvent.selectOptions(screen.getByLabelText("lingua"), "en");
    expect(await screen.findByRole("heading", { name: "Raffle Generator" })).toBeInTheDocument();
    expect(document.documentElement.lang).toBe("en");
  });

  it("sem prefixo no URL ignora a língua guardada: o português manda sempre", async () => {
    localStorage.setItem("rifas.lingua", "en");
    render(
      <ProvedorI18n>
        <Amostra />
      </ProvedorI18n>,
    );
    expect(await screen.findByRole("heading", { name: "Gerador de Rifas" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/"); // nunca se reescreve para /en
  });

  it("sem prefixo no URL, uma língua por defeito do servidor diferente de português não muda nada (GEO/SEO)", async () => {
    const servidor = new ServidorFalso();
    servidor.porDefeito = "en";
    servidor.instalar();
    render(
      <ProvedorI18n>
        <Amostra />
      </ProvedorI18n>,
    );
    expect(await screen.findByRole("heading", { name: "Gerador de Rifas" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/"); // nunca se reescreve para /en
  });

  it("a língua do URL ganha à guardada, e mudar de língua põe o prefixo no URL (o português não leva)", async () => {
    localStorage.setItem("rifas.lingua", "pt");
    window.history.replaceState(null, "", "/en/tutorial?p=2");
    render(
      <ProvedorI18n>
        <Amostra />
      </ProvedorI18n>,
    );
    expect(await screen.findByRole("heading", { name: "Raffle Generator" })).toBeInTheDocument();
    expect(window.location.pathname + window.location.search).toBe("/en/tutorial?p=2"); // sem mexer no que já está certo
    await userEvent.selectOptions(screen.getByLabelText("lingua"), "pt");
    await waitFor(() => expect(window.location.pathname).toBe("/tutorial"));
    expect(window.location.search).toBe("?p=2");
    await userEvent.selectOptions(screen.getByLabelText("lingua"), "en");
    await waitFor(() => expect(window.location.pathname).toBe("/en/tutorial"));
  });

  it("a língua escolhida no seletor passa a estar no URL; o painel nunca leva prefixo", async () => {
    window.history.replaceState(null, "", "/sobre");
    const { unmount } = render(
      <ProvedorI18n>
        <Amostra />
      </ProvedorI18n>,
    );
    expect(await screen.findByRole("heading", { name: "Gerador de Rifas" })).toBeInTheDocument();
    await userEvent.selectOptions(screen.getByLabelText("lingua"), "en");
    await waitFor(() => expect(window.location.pathname).toBe("/en/sobre"));
    unmount();
    window.history.replaceState(null, "", "/en/admin"); // o painel nunca leva prefixo, mesmo escolhendo outra língua
    render(
      <ProvedorI18n>
        <Amostra />
      </ProvedorI18n>,
    );
    expect(await screen.findByRole("heading", { name: "Raffle Generator" })).toBeInTheDocument();
    await waitFor(() => expect(window.location.pathname).toBe("/admin"));
  });

  it("pede /api/textos em paralelo com /api/linguas (não em série, para não perder tempo no LCP)", async () => {
    const servidor = new ServidorFalso();
    let resolverLinguas: () => void = () => {};
    const atrasoLinguas = new Promise<void>((r) => {
      resolverLinguas = r;
    });
    const original = servidor.manejar;
    servidor.manejar = async (entrada, init) => {
      const url = typeof entrada === "string" ? entrada : entrada.toString();
      if (url === "/api/linguas") await atrasoLinguas;
      return original(entrada, init);
    };
    servidor.instalar();
    render(
      <ProvedorI18n>
        <Amostra />
      </ProvedorI18n>,
    );
    // os textos já chegaram (o título aparece) mesmo com /api/linguas ainda pendurado: se fosse em série, isto
    // nunca resolvia (o pedido dos textos só partia depois de /api/linguas responder)
    expect(await screen.findByRole("heading", { name: "Gerador de Rifas" })).toBeInTheDocument();
    expect(screen.getByLabelText("lingua").querySelectorAll("option")).toHaveLength(0);
    resolverLinguas();
    await waitFor(() =>
      expect(screen.getByLabelText("lingua").querySelectorAll("option").length).toBeGreaterThan(0),
    );
  });

  it("mostra o erro se a API falhar", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve(new Response(JSON.stringify({ detail: "servidor em baixo" }), { status: 503 })),
      ),
    );
    render(
      <ProvedorI18n>
        <Amostra />
      </ProvedorI18n>,
    );
    expect(await screen.findByRole("alert")).toHaveTextContent("servidor em baixo");
  });
});
