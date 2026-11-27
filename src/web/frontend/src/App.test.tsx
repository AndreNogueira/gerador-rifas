import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import type { Sessao, Trabalho } from "./api";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

let servidor: ServidorFalso;

function abrir() {
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
}
const t = (id: string) => screen.getByTestId(id);
const ficheiro = (nome: string, tipo = "application/pdf") => new File(["%PDF-1.4 x"], nome, { type: tipo });

async function carregarTemplateEAlgarismos() {
  await userEvent.upload(t("upload-template"), ficheiro("Rifa Natal.pdf"));
  await waitFor(() => expect(t("estado-template")).toHaveTextContent("5 bilhetes"));
  await userEvent.upload(t("upload-algarismos"), ficheiro("digitos.png", "image/png"));
  await waitFor(() => expect(t("estado-algarismos")).toHaveTextContent("digitos.png"));
}

const gerando = (extra: Partial<Trabalho> = {}): Trabalho => ({
  estado: "a_gerar",
  texto: "A gerar…",
  cor: "suave",
  feitas: 0,
  total: 0,
  registo: [],
  proximo: 0,
  erro: "",
  entrega: null,
  ...extra,
});

beforeEach(() => {
  localStorage.clear();
  servidor = new ServidorFalso().instalar();
});
afterEach(() => vi.unstubAllGlobals());

describe("sessão", () => {
  it("cria uma sessão, guarda-lhe o id e retoma-a ao recarregar", async () => {
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(localStorage.getItem("rifas.sessao")).toBe("sessao1"));
    expect(servidor.chamadas("POST", /\/api\/sessoes$/)).toHaveLength(1);
    document.body.innerHTML = "";
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() =>
      expect(servidor.chamadas("GET", /\/api\/sessoes\/sessao1\?desde=0$/).length).toBeGreaterThan(0),
    );
    expect(servidor.chamadas("POST", /\/api\/sessoes$/)).toHaveLength(1); // não criou outra
  });

  it("se o servidor perdeu a sessão, cria outra e avisa", async () => {
    localStorage.setItem("rifas.sessao", "antiga");
    abrir();
    expect(await screen.findByTestId("dialogo-texto")).toHaveTextContent("A sessão expirou.");
    await waitFor(() => expect(localStorage.getItem("rifas.sessao")).toBe("sessao1"));
  });

  it("pede ao servidor na língua escolhida (X-Lingua) e volta a pedir o estado quando ela muda", async () => {
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await userEvent.selectOptions(t("lingua"), "en");
    expect(await screen.findByRole("heading", { name: "Raffle Generator" })).toBeInTheDocument();
    await waitFor(() =>
      expect(servidor.chamadas("GET", /sessao1\?desde=0/).some((p) => p.lingua === "en")).toBe(true),
    );
  });
});

describe("carregar ficheiros", () => {
  it("mostra o estado do template e dos algarismos e o visor com o template", async () => {
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
    // os <input type="file"> escondidos têm o mesmo rótulo do botão visível que lhes dá o clique, não só este
    // (o atributo "hidden" tira-os da árvore de acessibilidade do browser, mas algumas ferramentas leem o atributo direto do DOM)
    expect(t("upload-template")).toHaveAttribute("aria-label", expect.stringContaining("Canva"));
    expect(t("upload-algarismos")).toHaveAttribute("aria-label", expect.stringContaining("PNG"));
    await carregarTemplateEAlgarismos();
    expect(servidor.chamadas("PUT", /template$/)[0]?.nome).toBe("Rifa Natal.pdf");
    expect(t("titulo-visor")).toHaveTextContent("Template");
    expect(t("visor")).toHaveAttribute("src", "/api/sessoes/sessao1/modelo.pdf#view=FitH");
    expect(t("previa")).toBeEnabled();
    expect(t("gerar")).toBeEnabled();
  });

  it("o título do passo 2 só diz «(obrigatório)» enquanto o campo está vazio", async () => {
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
    expect(screen.getByRole("region", { name: "Algarismos (obrigatório)" })).toBeInTheDocument();
    await carregarTemplateEAlgarismos();
    expect(screen.queryByRole("region", { name: "Algarismos (obrigatório)" })).not.toBeInTheDocument();
    expect(screen.getByRole("region", { name: "Algarismos" })).toBeInTheDocument();
  });

  it("sem template os botões de pré-visualizar e gerar estão desativados", async () => {
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(t("estado-template")).toHaveTextContent("Escolha o PDF do template."));
    expect(t("previa")).toBeDisabled();
    expect(t("gerar")).toBeDisabled();
  });

  it("um template recusado mostra a mensagem completa num diálogo", async () => {
    servidor.respostaTemplate = (s, nome) => ({
      ...s,
      template: {
        nome,
        estado: "erro",
        texto: "✖ Não consegui abrir o PDF.",
        detalhe: `Não consegui abrir o PDF do template:\n«${nome}»`,
      },
    });
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
    await userEvent.upload(t("upload-template"), ficheiro("mau.pdf"));
    expect(await screen.findByTestId("dialogo-texto")).toHaveTextContent("«mau.pdf»");
    expect(t("estado-template")).toHaveTextContent("✖ Não consegui abrir o PDF.");
    await userEvent.click(t("dialogo-ok"));
    await waitFor(() => expect(screen.queryByTestId("dialogo-texto")).not.toBeInTheDocument());
  });

  it("um template de uma só rifa mostra o painel da folha", async () => {
    servidor.respostaTemplate = (s, nome) => ({
      ...s,
      template: { nome, estado: "ok", texto: "✔ Template com 1 rifa", detalhe: "" },
      info: { n_campos: 1, primeiro: "0001", ultimo: "0001", digitos: 4, tem_folha: true },
    });
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
    expect(screen.queryByTestId("papel")).not.toBeInTheDocument();
    await userEvent.upload(t("upload-template"), ficheiro("uma.pdf"));
    expect(await screen.findByTestId("papel")).toBeInTheDocument();
    expect(screen.getByTestId("margem")).toHaveValue("5");
  });

  it("os algarismos do desenho passam a ser os do template novo", async () => {
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
    await userEvent.clear(t("algarismos"));
    await userEvent.type(t("algarismos"), "7");
    await userEvent.upload(t("upload-template"), ficheiro("a.pdf"));
    await waitFor(() => expect(t("algarismos")).toHaveValue("4"));
  });
});

describe("formulário", () => {
  it("recalcula o resumo no servidor quando se escreve", async () => {
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(t("resumo")).toHaveTextContent("1000 números"));
    await userEvent.clear(t("ate"));
    await userEvent.type(t("ate"), "50");
    await waitFor(() => expect(t("resumo")).toHaveTextContent("50 números"));
  });

  it("lembra números e modo, mas nunca o nome dos ficheiros", async () => {
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(t("nome")).toBeInTheDocument());
    await userEvent.type(t("nome"), "Rifa Secreta");
    await userEvent.clear(t("ate"));
    await userEvent.type(t("ate"), "250");
    await userEvent.click(screen.getByRole("radio", { name: "Um único PDF" }));
    await waitFor(() => expect(localStorage.getItem("rifas.campos")).toContain("250"));
    const guardado = JSON.parse(localStorage.getItem("rifas.campos") ?? "{}");
    expect(guardado).toMatchObject({ fim: "250", modo: "unico" });
    expect(JSON.stringify(guardado)).not.toContain("Secreta");
    expect(t("max-ficheiro")).toBeDisabled(); // só conta no modo «vários»
  });
});

describe("pré-visualizar e gerar", () => {
  it("a pré-visualização aparece no visor com o título do servidor", async () => {
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
    await carregarTemplateEAlgarismos();
    await userEvent.click(t("previa"));
    await waitFor(() => expect(t("titulo-visor")).toHaveTextContent("números 1 a 5"));
    expect(t("visor").getAttribute("src")).toContain("/previa.pdf?n=1");
    expect(servidor.chamadas("POST", /previa$/)[0]?.corpo).toMatchObject({
      inicio: "1",
      fim: "1000",
      digitos: "4",
    });
  });

  it("gera: mostra o progresso e o registo, e no fim a ligação para descarregar", async () => {
    servidor.passos = [
      gerando({ feitas: 2, total: 10, texto: "2 / 10 páginas", registo: ["A gerar «A.pdf»…"], proximo: 1 }),
      {
        ...gerando({ feitas: 10, total: 10, registo: ["✔ A.pdf: 10 páginas"], proximo: 2 }),
        estado: "ok",
        texto: "✔ 1 PDF gerado.",
        cor: "ok",
        entrega: {
          tipo: "pdf",
          nome: "A.pdf",
          ficheiros: ["A.pdf"],
          total: 1,
          url: "/api/sessoes/sessao1/descarregar",
        },
      },
    ];
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
    await carregarTemplateEAlgarismos();
    await userEvent.type(t("nome"), "A");
    await userEvent.click(t("gerar"));
    await waitFor(() => expect(t("gerar")).toHaveTextContent("Cancelar"));
    expect(t("upload-template")).toBeDisabled; // nada se carrega a meio
    await waitFor(() => expect(t("estado")).toHaveTextContent("2 / 10 páginas"));
    expect(t("registo")).toHaveTextContent("A gerar «A.pdf»…");
    await waitFor(() => expect(t("estado")).toHaveTextContent("✔ 1 PDF gerado."), { timeout: 4000 });
    expect(t("registo")).toHaveTextContent("✔ A.pdf: 10 páginas");
    expect(t("gerar")).toHaveTextContent("Gerar PDFs");
    const ligacao = t("descarregar");
    expect(ligacao).toHaveAttribute("href", "/api/sessoes/sessao1/descarregar");
    expect(ligacao).toHaveTextContent("Descarregar — A.pdf");
    expect(t("progresso")).toHaveValue(1);
  });

  it("depois de descarregar convida a deixar um comentário, uma só vez por aparelho, e dispensa-se", async () => {
    localStorage.removeItem("rifas.convite");
    servidor.passos = [
      {
        ...gerando({ feitas: 10, total: 10, registo: ["✔ A.pdf: 10 páginas"], proximo: 1 }),
        estado: "ok",
        texto: "✔ 1 PDF gerado.",
        cor: "ok",
        entrega: {
          tipo: "pdf",
          nome: "A.pdf",
          ficheiros: ["A.pdf"],
          total: 1,
          url: "/api/sessoes/sessao1/descarregar",
        },
      },
    ];
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
    await carregarTemplateEAlgarismos();
    await userEvent.type(t("nome"), "A");
    await userEvent.click(t("gerar"));
    const ligacao = await screen.findByTestId("descarregar", {}, { timeout: 4000 });
    expect(screen.queryByTestId("convite-comentario")).toBeNull(); // só depois de descarregar, não antes
    ligacao.addEventListener("click", (e) => e.preventDefault()); // o jsdom não navega
    await userEvent.click(ligacao);
    const convite = await screen.findByTestId("convite-comentario");
    expect(convite).toHaveAttribute("role", "status"); // um aviso, não uma janela
    expect(convite).toHaveTextContent("Gostou? Diga-nos o que achou.");
    expect(screen.getByTestId("convite-abrir")).toHaveAttribute("href", "/opiniao");
    expect(localStorage.getItem("rifas.convite")).toBe("1");
    await userEvent.click(screen.getByTestId("convite-depois"));
    expect(screen.queryByTestId("convite-comentario")).toBeNull();
    await userEvent.click(ligacao); // descarregar outra vez: já não convida
    expect(screen.queryByTestId("convite-comentario")).toBeNull();
  });

  it("quem já foi convidado neste aparelho não volta a ver o convite", async () => {
    localStorage.setItem("rifas.convite", "1");
    servidor.passos = [
      {
        ...gerando({ feitas: 10, total: 10, registo: ["✔ A.pdf: 10 páginas"], proximo: 1 }),
        estado: "ok",
        texto: "✔ 1 PDF gerado.",
        cor: "ok",
        entrega: {
          tipo: "pdf",
          nome: "A.pdf",
          ficheiros: ["A.pdf"],
          total: 1,
          url: "/api/sessoes/sessao1/descarregar",
        },
      },
    ];
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
    await carregarTemplateEAlgarismos();
    await userEvent.type(t("nome"), "A");
    await userEvent.click(t("gerar"));
    const ligacao = await screen.findByTestId("descarregar", {}, { timeout: 4000 });
    ligacao.addEventListener("click", (e) => e.preventDefault());
    await userEvent.click(ligacao);
    expect(screen.queryByTestId("convite-comentario")).toBeNull();
    localStorage.removeItem("rifas.convite");
  });

  it("cancelar pede o cancelamento ao servidor", async () => {
    servidor.passos = [gerando({ feitas: 1, total: 100 })];
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
    await carregarTemplateEAlgarismos();
    await userEvent.type(t("nome"), "A");
    await userEvent.click(t("gerar"));
    await waitFor(() => expect(t("gerar")).toHaveTextContent("Cancelar"));
    await userEvent.click(t("gerar"));
    await waitFor(() => expect(servidor.chamadas("POST", /cancelar$/)).toHaveLength(1));
    await waitFor(() => expect(t("estado")).toHaveTextContent("A cancelar…"));
    expect(t("gerar")).toBeDisabled();
  });

  it("uma geração que falha mostra o erro num diálogo", async () => {
    servidor.passos = [
      gerando({ feitas: 1, total: 10 }),
      {
        ...gerando(),
        estado: "falhou",
        texto: "✖ Falhou.",
        cor: "erro",
        erro: "Erro inesperado: sem memória",
      },
    ];
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
    await carregarTemplateEAlgarismos();
    await userEvent.type(t("nome"), "A");
    await userEvent.click(t("gerar"));
    expect(await screen.findByTestId("dialogo-texto", undefined, { timeout: 4000 })).toHaveTextContent(
      "sem memória",
    );
  });

  it("um erro de rede mostra uma mensagem clara em vez de rebentar", async () => {
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
    await carregarTemplateEAlgarismos();
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.reject(new TypeError("Failed to fetch"))),
    );
    await userEvent.click(t("previa"));
    expect(await screen.findByTestId("dialogo-texto")).toHaveTextContent("Sem ligação ao servidor.");
  });
});

describe("limpar tudo", () => {
  it("apaga a sessão no servidor, cria outra e repõe o formulário", async () => {
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(t("upload-template")).toBeInTheDocument());
    await carregarTemplateEAlgarismos();
    await userEvent.type(t("nome"), "Rifa");
    await userEvent.clear(t("ate"));
    await userEvent.type(t("ate"), "77");
    await userEvent.click(t("limpar"));
    await waitFor(() => expect(servidor.chamadas("DELETE", /sessao1$/)).toHaveLength(1));
    await waitFor(() => expect(localStorage.getItem("rifas.sessao")).toBe("sessao2"));
    await waitFor(() => expect(t("estado-template")).toHaveTextContent("Escolha o PDF do template."));
    expect(t("nome")).toHaveValue("");
    expect(t("ate")).toHaveValue("1000");
  });
});

describe("páginas", () => {
  it("o «Acerca de» mostra a versão e o texto comprido do site, sem a linha das bibliotecas do Windows", async () => {
    window.history.pushState(null, "", "/sobre");
    abrir();
    await waitFor(() => expect(screen.getByTestId("sobre-texto")).toHaveTextContent("Versão 3.0.0"));
    expect(t("sobre-texto")).not.toHaveTextContent("Usa X.");
    const corpo = t("sobre-corpo");
    expect(corpo.querySelectorAll("p")).toHaveLength(3); // um parágrafo por assunto…
    expect(corpo.querySelector("p strong")).toHaveTextContent("Para quem é."); // …com o título a negrito
    expect(corpo).toHaveTextContent("Gerador de Rifas é para escolas"); // {app} preenchido
    window.history.pushState(null, "", "/");
  });

  it("o «Acerca de» só diz quem o faz com RESPONSAVEL configurado no servidor", async () => {
    servidor.responsavel = "Nome de Teste";
    window.history.pushState(null, "", "/sobre");
    abrir();
    const corpo = await screen.findByTestId("sobre-corpo");
    await waitFor(() => expect(corpo).toHaveTextContent("Nome de Teste"));
    expect(corpo.querySelectorAll("p")).toHaveLength(4); // os 3 de sempre + «quem o faz»
    window.history.pushState(null, "", "/");
  });

  it("uma rota desconhecida mostra um 404 a sério, nunca o gerador escondido", async () => {
    window.history.pushState(null, "", "/isto-nao-existe");
    abrir();
    await screen.findByTestId("pagina-404");
    expect(screen.queryByTestId("nome")).not.toBeInTheDocument(); // o campo do gerador nao esta la
    expect(document.title).toBe("Página não encontrada | Gerador de Rifas");
    await userEvent.click(within(document.body).getByRole("link", { name: /Voltar/ }));
    await waitFor(() => expect(window.location.pathname).toBe("/"));
    window.history.pushState(null, "", "/");
  });

  it("navega entre o ecrã principal e as outras páginas sem perder o que está escrito", async () => {
    window.history.pushState(null, "", "/");
    abrir();
    await screen.findByRole("heading", { name: "Gerador de Rifas" });
    await waitFor(() => expect(t("nome")).toBeInTheDocument());
    await userEvent.type(t("nome"), "Rifa");
    await userEvent.click(t("nav-sobre"));
    expect(await screen.findByTestId("sobre-texto")).toBeInTheDocument();
    expect(window.location.pathname).toBe("/sobre");
    await userEvent.click(within(document.body).getByRole("link", { name: /Voltar/ }));
    await waitFor(() => expect(t("nome")).toHaveValue("Rifa"));
    expect(window.location.pathname).toBe("/");
  });
});

describe("sessão devolvida pelo servidor", () => {
  it("o tipo Sessao tem o que o ecrã usa (guarda contra mudanças na API)", () => {
    const s: Sessao = new ServidorFalso().nova();
    expect(Object.keys(s).sort()).toEqual(
      [
        "algarismos",
        "avisos",
        "info",
        "logotipo",
        "modelo_url",
        "previa",
        "pronto",
        "sessao",
        "template",
        "tem_modelo",
        "trabalho",
      ].sort(),
    );
  });
});
