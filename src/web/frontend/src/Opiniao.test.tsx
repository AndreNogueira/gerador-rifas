import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { App } from "./App";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

let servidor: ServidorFalso;

function abrir(caminho: string) {
  window.history.pushState({}, "", caminho);
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
}

beforeEach(() => {
  localStorage.clear();
  servidor = new ServidorFalso();
  servidor.instalar();
});

describe("as páginas aparecem bem à vista", () => {
  it("o rodapé liga os comentários, o deixar um comentário e o reportar problema", async () => {
    abrir("/");
    const rodape = await screen.findByRole("navigation", { name: "Informação" });
    expect(within(rodape).getByRole("link", { name: "Comentários" })).toHaveAttribute("href", "/comentarios");
    expect(within(rodape).getByRole("link", { name: "Deixar um comentário" })).toHaveAttribute(
      "href",
      "/opiniao",
    );
    expect(within(rodape).getByRole("link", { name: "Reportar problema" })).toHaveAttribute(
      "href",
      "/reportar-problema",
    );
  });

  it("o cabeçalho tem os botões «Comentários» e «Reportar problema»", async () => {
    abrir("/");
    expect(await screen.findByTestId("nav-comentarios")).toHaveAttribute("href", "/comentarios");
    expect(screen.getByTestId("nav-reportar-problema")).toHaveAttribute("href", "/reportar-problema");
  });

  it("o título do separador segue a página", async () => {
    abrir("/comentarios");
    await waitFor(() => expect(document.title).toBe("Comentários | Gerador de Rifas"));
  });
});

describe("a página «Comentários»", () => {
  it("sem comentários convida a ser a primeira pessoa", async () => {
    abrir("/comentarios");
    expect(await screen.findByTestId("comentarios-vazio")).toHaveTextContent("Ainda não há comentários");
    expect(screen.getByTestId("comentarios-escrever")).toHaveAttribute("href", "/opiniao");
  });

  it("mostra anónimos, nomes escolhidos e «Visitante n.º», e pagina com «Ver mais»", async () => {
    servidor.comentarios = [
      { id: "a", criado: 1_800_000_005, anonimo: true, nome: "", visitante: 0, texto: "Muito bom!" },
      {
        id: "b",
        criado: 1_800_000_004,
        anonimo: false,
        nome: "Ana",
        visitante: 0,
        texto: "Ajudou a escola.",
      },
      {
        id: "c",
        criado: 1_800_000_003,
        anonimo: false,
        nome: "",
        visitante: 4321,
        texto: "Falta um tema verde.",
      },
    ];
    abrir("/comentarios");
    await screen.findAllByTestId("comentario");
    expect(screen.getAllByTestId("comentario")).toHaveLength(2);
    const [primeiro, segundo] = screen.getAllByTestId("comentario");
    expect(primeiro).toHaveTextContent("Anónimo(a)");
    expect(primeiro).toHaveTextContent("Muito bom!");
    expect(segundo).toHaveTextContent("Ana");
    await userEvent.click(screen.getByTestId("comentarios-mais"));
    await waitFor(() => expect(screen.getAllByTestId("comentario")).toHaveLength(3));
    expect(screen.getAllByTestId("comentario")[2]).toHaveTextContent("Visitante n.º 4321");
    expect(screen.queryByTestId("comentarios-mais")).toBeNull();
    expect(servidor.pedidos.filter((p) => p.url.startsWith("/api/comentarios")).map((p) => p.url)).toEqual([
      "/api/comentarios",
      "/api/comentarios?antes=1800000004~b",
    ]);
  });

  it("o texto de um comentário nunca é interpretado como HTML", async () => {
    servidor.comentarios = [
      {
        id: "x",
        criado: 1_800_000_000,
        anonimo: true,
        nome: "",
        visitante: 0,
        texto: '<img src=x onerror="alert(1)"><b>negrito</b>',
      },
    ];
    abrir("/comentarios");
    const c = await screen.findByTestId("comentario");
    expect(c.querySelector("img, b")).toBeNull();
    expect(c).toHaveTextContent('<img src=x onerror="alert(1)">');
  });
});

describe("a página «Deixar um comentário»", () => {
  it("por omissão é anónimo e envia só o texto", async () => {
    abrir("/opiniao");
    expect(await screen.findByTestId("opiniao-anonimo")).toBeChecked();
    expect(screen.queryByTestId("opiniao-nome")).toBeNull();
    await userEvent.type(screen.getByTestId("opiniao-texto"), "Gostei muito da aplicação.");
    await userEvent.click(screen.getByTestId("opiniao-enviar"));
    expect(await screen.findByTestId("comentario-enviado")).toHaveTextContent("Obrigado!");
    expect(servidor.comentariosEnviados).toEqual([
      { texto: "Gostei muito da aplicação.", anonimo: true, nome: "", site: "" },
    ]);
    expect(screen.getByTestId("comentario-ver")).toHaveAttribute("href", "/comentarios");
  });

  it("escolher mostrar um nome abre o campo e envia-o; voltar ao anónimo não envia nome nenhum", async () => {
    abrir("/opiniao");
    await userEvent.click(await screen.findByTestId("opiniao-com-nome"));
    await userEvent.type(screen.getByTestId("opiniao-nome"), "Rui");
    await userEvent.click(screen.getByTestId("opiniao-anonimo"));
    expect(screen.queryByTestId("opiniao-nome")).toBeNull();
    await userEvent.type(screen.getByTestId("opiniao-texto"), "Texto de teste um");
    await userEvent.click(screen.getByTestId("opiniao-enviar"));
    await screen.findByTestId("comentario-enviado");
    expect(servidor.comentariosEnviados[0]).toMatchObject({ anonimo: true, nome: "" });

    servidor.comentariosEnviados = [];
    abrir("/opiniao");
  });

  it("com nome envia o nome escolhido", async () => {
    abrir("/opiniao");
    await userEvent.click(await screen.findByTestId("opiniao-com-nome"));
    await userEvent.type(screen.getByTestId("opiniao-nome"), "Rui");
    await userEvent.type(screen.getByTestId("opiniao-texto"), "Texto de teste dois");
    await userEvent.click(screen.getByTestId("opiniao-enviar"));
    await screen.findByTestId("comentario-enviado");
    expect(servidor.comentariosEnviados[0]).toMatchObject({
      anonimo: false,
      nome: "Rui",
      texto: "Texto de teste dois",
    });
  });

  it("um texto curto não chega a ir ao servidor", async () => {
    abrir("/opiniao");
    await userEvent.type(await screen.findByTestId("opiniao-texto"), "oi");
    await userEvent.click(screen.getByTestId("opiniao-enviar"));
    expect(await screen.findByTestId("opiniao-erro")).toHaveTextContent("Escreva pelo menos 5 letras.");
    expect(servidor.comentariosEnviados).toHaveLength(0);
  });

  it("um erro do servidor (demasiados envios) mostra-se e o texto não se perde", async () => {
    servidor.comentarioErro = "Enviou muitas mensagens seguidas. Tente outra vez daqui a pouco.";
    abrir("/opiniao");
    await userEvent.type(await screen.findByTestId("opiniao-texto"), "Texto que não se pode perder");
    await userEvent.click(screen.getByTestId("opiniao-enviar"));
    expect(await screen.findByTestId("opiniao-erro")).toHaveTextContent("Enviou muitas mensagens");
    expect(screen.getByTestId("opiniao-texto")).toHaveValue("Texto que não se pode perder");
  });

  it("explica o que se faz ao IP e liga a política de privacidade; o campo-isco está escondido das pessoas", async () => {
    abrir("/opiniao");
    await screen.findByTestId("pagina-opiniao");
    expect(screen.getByText(/endereço IP fica guardado apenas para o responsável/)).toBeInTheDocument();
    expect(
      within(screen.getByTestId("pagina-opiniao")).getByRole("link", { name: "Privacidade" }),
    ).toHaveAttribute("href", "/privacidade");
    const isco = document.querySelector(".isco");
    expect(isco).toHaveAttribute("aria-hidden", "true");
    expect(isco?.querySelector("input")).toHaveAttribute("tabindex", "-1");
  });
});

describe("a página «Reportar problema»", () => {
  const preencher = async () => {
    await userEvent.type(await screen.findByTestId("problema-resumo"), "O botão Gerar não faz nada");
    await userEvent.type(screen.getByTestId("problema-descricao"), "Carrego em Gerar e nada acontece.");
  };

  it("sem o GitHub ligado avisa e não deixa abrir", async () => {
    servidor.problemasAtivos = false;
    abrir("/reportar-problema");
    expect(await screen.findByTestId("problema-inativo")).toHaveTextContent("ainda não está ativa");
    expect(screen.getByTestId("problema-abrir")).toBeDisabled();
  });

  it("«Abrir» cria o problema e mostra o número", async () => {
    abrir("/reportar-problema");
    await preencher();
    await userEvent.type(screen.getByTestId("problema-passos"), "1. carregar o template");
    await userEvent.click(screen.getByTestId("problema-abrir"));
    expect(await screen.findByTestId("problema-registado")).toHaveTextContent("n.º 42");
    expect(servidor.problemasEnviados[0]).toMatchObject({
      resumo: "O botão Gerar não faz nada",
      descricao: "Carrego em Gerar e nada acontece.",
      passos: "1. carregar o template",
      tecnica: "", // a informação técnica só vai se a pessoa marcar
      site: "",
    });
  });

  it("marcar a informação técnica junta o navegador e o ecrã", async () => {
    abrir("/reportar-problema");
    await preencher();
    await userEvent.click(screen.getByTestId("problema-tecnica"));
    await userEvent.click(screen.getByTestId("problema-abrir"));
    await screen.findByTestId("problema-registado");
    const enviado = servidor.problemasEnviados[0] as { tecnica: string };
    expect(enviado.tecnica).toMatch(/ecrã \d+x\d+ \| janela \d+x\d+/);
    expect(enviado.tecnica.length).toBeLessThanOrEqual(600);
  });

  it("campos curtos não chegam ao servidor", async () => {
    abrir("/reportar-problema");
    await userEvent.type(await screen.findByTestId("problema-resumo"), "curto");
    await userEvent.type(screen.getByTestId("problema-descricao"), "também curto");
    await userEvent.click(screen.getByTestId("problema-abrir"));
    expect(await screen.findByTestId("problema-erro")).toHaveTextContent("pelo menos 10 letras");
    expect(servidor.problemasEnviados).toHaveLength(0);
  });

  it("se o GitHub falhar mostra o aviso e conserva o que se escreveu", async () => {
    servidor.problemaErro = "Não foi possível registar o problema agora. Tente outra vez daqui a pouco.";
    abrir("/reportar-problema");
    await preencher();
    await userEvent.click(screen.getByTestId("problema-abrir"));
    expect(await screen.findByTestId("problema-erro")).toHaveTextContent("Não foi possível registar");
    expect(screen.getByTestId("problema-resumo")).toHaveValue("O botão Gerar não faz nada");
  });
});
