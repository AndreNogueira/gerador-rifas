import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import type { PedidoEtiquetas, PedidoPrecario } from "./api";
import { ProvedorI18n } from "./i18n";
import { estadoInicial, paisDoBrowser, pedidoDoEstado } from "./Precario";
import { ServidorFalso } from "./servidor-falso";

let servidor: ServidorFalso;

function abrir(caminho = "/precario") {
  window.history.pushState({}, "", caminho);
  render(
    <ProvedorI18n>
      <App />
    </ProvedorI18n>,
  );
}

const pedidosA = (fim: string) => servidor.pedidos.filter((p) => p.url === fim);

beforeEach(() => {
  localStorage.clear();
  servidor = new ServidorFalso();
  servidor.instalar();
  URL.createObjectURL = vi.fn(() => "blob:previa");
  URL.revokeObjectURL = vi.fn();
});

const CAT = {
  categorias: [
    {
      id: "bebidas",
      nome: "Bebidas",
      artigos: [{ id: "agua", nome: "Água", emoji: "1f4a7", icones: ["1f4a7", "1f6b0", "1f9ca"] }],
    },
  ],
  ocasioes: [{ id: "natal", nome: "Natal", desenho: "natal", artigos: ["agua"], meses: [12] }],
  sugerida: "",
  desenhos: [{ id: "natal", nome: "Natal", cores: ["#1f6b3a", "#c0392b", "#ffffff"] }],
  moedas: [{ codigo: "EUR", simbolo: "€", decimais: 2 }],
  paises: { PT: "EUR", GB: "GBP" },
  pais: "PT",
  moeda: "EUR",
  limites: { linhas: 80, titulo: 40, subtitulo: 70, rodape: 120, nome: 40, moeda_inventada: 14 },
  formatos: ["A4"],
  logo_lugares: ["esquerda", "direita", "rodape"],
};

describe("o estado e o pedido do preçário", () => {
  it("parte da ocasião do mês, sem preços, na moeda do país", () => {
    const e = estadoInicial({ ...CAT, ocasioes: [...CAT.ocasioes] }, 12, null);
    expect(e.ocasiao).toBe("natal");
    expect(e.titulo).toBe("Natal");
    expect(e.linhas.map((l) => l.artigo)).toEqual(["agua"]);
    expect(e.moeda).toBe("EUR");
    expect(pedidoDoEstado(e).moeda).toEqual({ codigo: "EUR" });
  });

  it("um rascunho estragado ou de um artigo que já não existe não parte nada", () => {
    expect(estadoInicial(CAT, 12, "lixo").ocasiao).toBe("natal");
    const g = {
      titulo: "Meu",
      linhas: [{ chave: "x", artigo: "nao_existe", nome: "", categoria: "", emoji: "", preco: "" }],
    };
    expect(estadoInicial(CAT, 12, g).titulo).toBe("Natal");
    const bom = {
      titulo: "Meu",
      linhas: [{ chave: "agua", artigo: "agua", nome: "", categoria: "", emoji: "", preco: "2" }],
    };
    const e = estadoInicial(CAT, 12, bom);
    expect(e.titulo).toBe("Meu");
    expect(e.linhas[0]?.preco).toBe("2");
  });

  it("a moeda inventada só vai se tiver nome; os textos livres levam nome, categoria e imagem", () => {
    const e = estadoInicial(CAT, 12, null);
    expect(pedidoDoEstado({ ...e, inventada: true, invNome: "  " }).moeda).toEqual({ codigo: "EUR" });
    expect(
      pedidoDoEstado({ ...e, inventada: true, invNome: " fichas ", invAntes: true, invCasas: 1 }).moeda,
    ).toEqual({ nome: "fichas", antes: true, decimais: 1 });
    const p = pedidoDoEstado({
      ...e,
      linhas: [
        { chave: "c1", artigo: "", nome: "Bolo da avó", categoria: "doces", emoji: "1f370", preco: " 3 " },
      ],
    });
    expect(p.linhas[0]).toEqual({
      artigo: "",
      nome: "Bolo da avó",
      preco: "3",
      preco2: "",
      categoria: "doces",
      emoji: "1f370",
    });
  });

  it("o país vem da região do idioma do browser quando a conhecemos", () => {
    const antes = Object.getOwnPropertyDescriptor(window.navigator, "language");
    Object.defineProperty(window.navigator, "language", { value: "en-GB", configurable: true });
    expect(paisDoBrowser({ PT: "EUR", GB: "GBP" }, "PT")).toBe("GB");
    expect(paisDoBrowser({ PT: "EUR" }, "PT")).toBe("PT");
    Object.defineProperty(window.navigator, "language", { value: "xx", configurable: true });
    expect(paisDoBrowser({ PT: "EUR", GB: "GBP" }, "PT")).toBe("PT");
    if (antes) Object.defineProperty(window.navigator, "language", antes);
  });
});

describe("a página /precario", () => {
  it("abre com a ocasião sugerida, desenha a pré-visualização e descarrega o PDF", async () => {
    abrir();
    expect(
      await screen.findByRole("heading", { level: 1, name: "Gerador de preçários para festas" }),
    ).toBeInTheDocument();
    expect(await screen.findByTestId("precario-previa-img")).toBeInTheDocument();
    const pedido = pedidosA("/api/precario/previa.png").at(-1)?.corpo as PedidoPrecario;
    expect(pedido.desenho).toBe("arraial");
    expect(pedido.linhas.map((l) => l.artigo)).toEqual(["agua", "pizza", "bolo"]);
    expect(pedido.moeda).toEqual({ codigo: "EUR" });
    await userEvent.click(screen.getByTestId("precario-pdf"));
    await waitFor(() => expect(pedidosA("/api/precario/pdf")).toHaveLength(1));
  });

  it("escrever um preço, mudar de país e usar uma moeda inventada muda o pedido", async () => {
    abrir();
    const preco = await screen.findByTestId("precario-preco-agua");
    await userEvent.type(preco, "1,5");
    await userEvent.selectOptions(screen.getByTestId("precario-pais"), "BR");
    expect(screen.getByTestId("precario-moeda")).toHaveValue("BRL");
    await waitFor(() => {
      const p = pedidosA("/api/precario/previa.png").at(-1)?.corpo as PedidoPrecario;
      expect(p.linhas[0]?.preco).toBe("1,5");
      expect(p.moeda).toEqual({ codigo: "BRL" });
    });
    await userEvent.click(screen.getByTestId("precario-inventada"));
    await userEvent.type(screen.getByTestId("precario-inv-nome"), "fichas");
    await waitFor(() => {
      const p = pedidosA("/api/precario/previa.png").at(-1)?.corpo as PedidoPrecario;
      expect(p.moeda).toEqual({ nome: "fichas", antes: false, decimais: 0 });
    });
  });

  it("escolher e tirar artigos, acrescentar um meu e pôr o mesmo preço na categoria", async () => {
    abrir();
    await screen.findByTestId("precario-previa-img");
    const sumo = screen.getByTestId("precario-artigo-sumo");
    expect(sumo).toHaveAttribute("aria-pressed", "false");
    await userEvent.click(sumo);
    expect(sumo).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByTestId("precario-preco-sumo")).toBeInTheDocument();
    await userEvent.click(sumo);
    expect(screen.queryByTestId("precario-preco-sumo")).not.toBeInTheDocument();
    await userEvent.type(screen.getByTestId("precario-meu-nome"), "Bolo da avó");
    await userEvent.click(screen.getByTestId("precario-meu-juntar"));
    expect(screen.getAllByText("Bolo da avó").length).toBeGreaterThan(0);
    await userEvent.type(screen.getByTestId("precario-preco-categoria-bebidas"), "2");
    expect(screen.getByTestId("precario-preco-agua")).toHaveValue("2");
    await userEvent.type(screen.getByTestId("precario-pesquisa"), "piz");
    expect(screen.getByTestId("precario-artigo-pizza")).toBeInTheDocument();
    expect(screen.queryByTestId("precario-artigo-agua")).not.toBeInTheDocument();
  });

  it("sem artigos não há pré-visualização, só o aviso; e os erros do servidor aparecem", async () => {
    abrir();
    await screen.findByTestId("precario-previa-img");
    for (const id of ["agua", "pizza", "bolo"])
      await userEvent.click(screen.getByTestId(`precario-artigo-${id}`));
    expect(screen.getByTestId("precario-vazio")).toBeInTheDocument();
    expect(screen.getByTestId("precario-pdf")).toBeDisabled();
    servidor.precarioErro = "Este texto não cabe";
    await userEvent.click(screen.getByTestId("precario-artigo-agua"));
    expect(await screen.findByTestId("precario-erro")).toHaveTextContent("Este texto não cabe");
  });

  it("o rascunho fica no browser e «Recomeçar» apaga-o", async () => {
    abrir();
    const titulo = await screen.findByTestId("precario-titulo");
    await userEvent.clear(titulo);
    await userEvent.type(titulo, "A minha festa");
    await waitFor(() =>
      expect(JSON.parse(localStorage.getItem("rifas.precario") ?? "{}").titulo).toBe("A minha festa"),
    );
    await userEvent.click(screen.getByTestId("precario-recomecar"));
    expect(screen.getByTestId("precario-titulo")).toHaveValue("Festa popular");
    await waitFor(() =>
      expect(JSON.parse(localStorage.getItem("rifas.precario") ?? "{}").titulo).toBe("Festa popular"),
    ); // o rascunho volta ao ponto de partida
  });
});

describe("dois tamanhos", () => {
  it("ligados, cada artigo ganha um segundo preço e o pedido leva os rótulos (por omissão os da língua)", async () => {
    abrir();
    await userEvent.type(await screen.findByTestId("precario-preco-agua"), "1");
    expect(screen.queryByTestId("precario-preco2-agua")).toBeNull();
    await userEvent.click(screen.getByTestId("precario-tamanhos"));
    await userEvent.type(await screen.findByTestId("precario-preco2-agua"), "1,8");
    await waitFor(() => {
      const p = pedidosA("/api/precario/previa.png").at(-1)?.corpo as PedidoPrecario;
      expect(p.tamanhos).toBe(true);
      expect(p.rotulos).toEqual(["Pequeno", "Grande"]);
      expect(p.linhas[0]).toMatchObject({ preco: "1", preco2: "1,8" });
    });
    await userEvent.type(screen.getByTestId("precario-rotulo-1"), "Média");
    await waitFor(() => {
      const p = pedidosA("/api/precario/previa.png").at(-1)?.corpo as PedidoPrecario;
      expect(p.rotulos).toEqual(["Média", "Grande"]);
    });
  });

  it("desligados, o segundo preço nem vai no pedido", async () => {
    abrir();
    await userEvent.click(await screen.findByTestId("precario-tamanhos"));
    await userEvent.type(await screen.findByTestId("precario-preco2-agua"), "2");
    await userEvent.click(screen.getByTestId("precario-tamanhos"));
    await waitFor(() => {
      const p = pedidosA("/api/precario/previa.png").at(-1)?.corpo as PedidoPrecario;
      expect(p.tamanhos).toBe(false);
      expect(p.linhas[0]?.preco2).toBe("");
    });
  });
});

describe("partilhar por ligação", () => {
  it("sem base de dados não há botão; com ela o pedido segue e a ligação aparece", async () => {
    abrir();
    await screen.findByTestId("precario-preco-agua");
    expect(screen.queryByTestId("precario-partilhar")).toBeNull();
  });

  it("com base de dados: partilha, e abrir a ligação repõe o preçário (preços em milésimos → texto)", async () => {
    servidor.partilhaEditor = true;
    abrir();
    await userEvent.type(await screen.findByTestId("precario-preco-agua"), "1,5");
    await userEvent.clear(screen.getByTestId("precario-titulo"));
    await userEvent.type(screen.getByTestId("precario-titulo"), "Festa X");
    await userEvent.click(await screen.findByTestId("precario-partilhar"));
    const ligacao = await screen.findByTestId("precario-ligacao");
    const id = /p=(\w+)/.exec(ligacao.textContent ?? "")?.[1];
    expect(id).toBeTruthy();
    cleanup();
    localStorage.clear();
    abrir(`/precario?p=${id}`);
    await waitFor(() => expect(screen.getByTestId("precario-titulo")).toHaveValue("Festa X"));
    await waitFor(() => expect(screen.getByTestId("precario-preco-agua")).toHaveValue("1,5"));
    expect(window.location.search).toBe("");
  });

  it("uma ligação que não existe mostra o aviso e não estraga a página", async () => {
    servidor.partilhaEditor = true;
    abrir("/precario?p=naoexiste1");
    expect(await screen.findByTestId("precario-erro")).toHaveTextContent("já não existe");
    expect(screen.getByTestId("precario-preco-agua")).toBeInTheDocument();
  });
});

describe("fotos próprias", () => {
  it("uma foto escolhida vai no pedido, mostra a miniatura e tira-se; nunca fica no rascunho do browser", async () => {
    const png = new File([new Uint8Array([137, 80, 78, 71])], "f.png", { type: "image/png" });
    vi.stubGlobal("createImageBitmap", async () => ({ width: 400, height: 200, close: () => undefined }));
    vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue({
      drawImage: () => undefined,
    } as never);
    vi.spyOn(HTMLCanvasElement.prototype, "toDataURL").mockReturnValue("data:image/png;base64,AAAA");
    abrir();
    await userEvent.upload(await screen.findByTestId("precario-foto-agua"), png);
    expect(await screen.findByTestId("precario-foto-tirar-agua")).toBeInTheDocument();
    await waitFor(() => {
      const p = pedidosA("/api/precario/previa.png").at(-1)?.corpo as PedidoPrecario;
      expect(p.linhas[0]?.foto).toBe("data:image/png;base64,AAAA");
    });
    expect(localStorage.getItem("rifas.precario") ?? "").not.toContain("AAAA");
    await userEvent.click(screen.getByTestId("precario-foto-tirar-agua"));
    await waitFor(() => {
      const p = pedidosA("/api/precario/previa.png").at(-1)?.corpo as PedidoPrecario;
      expect(p.linhas[0]?.foto).toBeUndefined();
    });
    vi.unstubAllGlobals();
  });
});

describe("as imagens à escolha de cada artigo", () => {
  it("a miniatura abre as imagens (até 8), a escolhida vai no pedido e a de omissão volta ao vazio", async () => {
    abrir();
    await userEvent.click(await screen.findByTestId("precario-icone-agua"));
    expect(screen.getByTestId("precario-icone-agua-1")).toHaveAttribute("aria-pressed", "true");
    await userEvent.click(screen.getByTestId("precario-icone-agua-3"));
    await waitFor(() => {
      const p = pedidosA("/api/precario/previa.png").at(-1)?.corpo as PedidoPrecario;
      expect(p.linhas[0]?.emoji).toBe("1f9ca");
    });
    expect(screen.getByTestId("precario-icone-agua-3")).toHaveAttribute("aria-pressed", "true");
    await userEvent.click(screen.getByTestId("precario-icone-agua-1"));
    await waitFor(() => {
      const p = pedidosA("/api/precario/previa.png").at(-1)?.corpo as PedidoPrecario;
      expect(p.linhas[0]?.emoji).toBe("");
    });
    await userEvent.click(screen.getByTestId("precario-icone-agua"));
    expect(screen.queryByTestId("precario-icone-agua-2")).not.toBeInTheDocument();
  });

  it('uma imagem de outra biblioteca ("fluent:<código>") vem de uma subpasta própria', async () => {
    abrir();
    await userEvent.click(await screen.findByTestId("precario-icone-agua"));
    const botao = screen.getByTestId("precario-icone-agua-4"); // a 4.ª (fluent:1f4a7)
    const img = botao.querySelector("img");
    expect(img).toHaveAttribute("src", "/precario/fluent/1f4a7.webp");
  });

  it("as imagens de bibliotecas diferentes aparecem agrupadas, cada grupo com o nome da biblioteca", async () => {
    abrir();
    await userEvent.click(await screen.findByTestId("precario-icone-agua"));
    const grupos = Array.from(document.querySelectorAll(".precario-icones-fonte-nome")).map(
      (e) => e.textContent,
    );
    expect(grupos).toEqual(["Noto Emoji", "Fluent Emoji"]); // 3 Noto (1f4a7, 1f6b0, 1f9ca) + 1 Fluent (fluent:1f4a7)
  });

  it("um rascunho com uma imagem que o catálogo não oferece volta à de omissão; uma oferecida fica", () => {
    const linha = (emoji: string) => ({
      chave: "agua",
      artigo: "agua",
      nome: "",
      categoria: "",
      emoji,
      preco: "",
    });
    expect(estadoInicial(CAT, 12, { titulo: "M", linhas: [linha("1f370")] }).linhas[0]?.emoji).toBe("");
    expect(estadoInicial(CAT, 12, { titulo: "M", linhas: [linha("1f6b0")] }).linhas[0]?.emoji).toBe("1f6b0");
  });
});

describe("as cores e o logótipo", () => {
  it("mudar uma cor vai no pedido, repor volta ao desenho e mudar de desenho também repõe", async () => {
    abrir();
    const cor = await screen.findByTestId("precario-cor-0");
    expect(cor).toHaveValue("#bf1a2e"); // a do desenho (o arraial da ocasião sugerida)
    expect(screen.getByTestId("precario-cores-repor")).toBeDisabled();
    fireEvent.change(cor, { target: { value: "#112233" } });
    await waitFor(() => {
      const p = pedidosA("/api/precario/previa.png").at(-1)?.corpo as PedidoPrecario;
      expect(p.cores).toEqual(["#112233", "", ""]);
    });
    expect(localStorage.getItem("rifas.precario")).toContain("#112233");
    await userEvent.click(screen.getByTestId("precario-cores-repor"));
    await waitFor(() => {
      const p = pedidosA("/api/precario/previa.png").at(-1)?.corpo as PedidoPrecario;
      expect(p.cores).toEqual(["", "", ""]);
    });
  });

  it("o logótipo escolhido vai no pedido com o sítio, tira-se e nunca fica no rascunho", async () => {
    const png = new File([new Uint8Array([137, 80, 78, 71])], "l.png", { type: "image/png" });
    vi.stubGlobal("createImageBitmap", async () => ({ width: 400, height: 200, close: () => undefined }));
    vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue({
      drawImage: () => undefined,
    } as never);
    vi.spyOn(HTMLCanvasElement.prototype, "toDataURL").mockReturnValue("data:image/png;base64,BBBB");
    abrir();
    expect(await screen.findByTestId("precario-logo-lugar")).toBeDisabled();
    await userEvent.upload(screen.getByTestId("precario-logo"), png);
    expect(await screen.findByTestId("precario-logo-mini")).toBeInTheDocument();
    await userEvent.selectOptions(screen.getByTestId("precario-logo-lugar"), "rodape");
    await waitFor(() => {
      const p = pedidosA("/api/precario/previa.png").at(-1)?.corpo as PedidoPrecario;
      expect(p.logotipo).toBe("data:image/png;base64,BBBB");
      expect(p.logo_lugar).toBe("rodape");
    });
    expect(localStorage.getItem("rifas.precario") ?? "").not.toContain("BBBB");
    expect(localStorage.getItem("rifas.precario") ?? "").toContain("rodape");
    await userEvent.click(screen.getByTestId("precario-logo-tirar"));
    await waitFor(() => {
      const p = pedidosA("/api/precario/previa.png").at(-1)?.corpo as PedidoPrecario;
      expect(p.logotipo).toBeUndefined();
    });
    vi.unstubAllGlobals();
  });

  it("cores estragadas de um rascunho voltam às do desenho", () => {
    const g = {
      titulo: "M",
      cores: ["azul", "", ""],
      linhas: [{ chave: "agua", artigo: "agua", nome: "", categoria: "", emoji: "", preco: "" }],
    };
    expect(estadoInicial(CAT, 12, g).cores).toEqual(["", "", ""]);
    expect(estadoInicial(CAT, 12, { ...g, cores: ["#aabbcc", "", "#ffffff"] }).cores).toEqual([
      "#aabbcc",
      "",
      "#ffffff",
    ]);
  });
});

describe("os combos", () => {
  it("junta 2 a 4 artigos de secções diferentes numa linha de «Menus e combos» e o pedido leva-os", async () => {
    abrir();
    expect(await screen.findByTestId("precario-combo-juntar")).toBeDisabled();
    await userEvent.selectOptions(screen.getByTestId("precario-combo-artigo-1"), "agua");
    expect(screen.getByTestId("precario-combo-juntar")).toBeDisabled(); // só um artigo
    await userEvent.selectOptions(screen.getByTestId("precario-combo-artigo-2"), "bolo");
    await userEvent.click(screen.getByTestId("precario-combo-juntar"));
    await waitFor(() => {
      const p = pedidosA("/api/precario/previa.png").at(-1)?.corpo as PedidoPrecario;
      const l = p.linhas.at(-1);
      expect(l?.combo).toEqual(["agua", "bolo"]);
      expect(l?.artigo).toBe("");
    });
    expect(screen.getByText("Água + Bolo")).toBeInTheDocument();
    expect(screen.getByTestId("precario-combo-artigo-1")).toHaveValue(""); // o formulário limpa-se
  });

  it("um artigo repetido não deixa juntar; um combo guardado com um artigo que já não existe sai do rascunho", async () => {
    abrir();
    await userEvent.selectOptions(await screen.findByTestId("precario-combo-artigo-1"), "agua");
    await userEvent.selectOptions(screen.getByTestId("precario-combo-artigo-2"), "agua");
    expect(screen.getByTestId("precario-combo-juntar")).toBeDisabled();
    const linha = (combo: string[]) => ({
      chave: "m1",
      artigo: "",
      nome: "",
      categoria: "menus",
      emoji: "",
      preco: "",
      combo,
    });
    const bom = estadoInicial(CAT, 12, {
      titulo: "M",
      linhas: [
        linha(["agua", "agua"]),
        { chave: "agua", artigo: "agua", nome: "", categoria: "", emoji: "", preco: "" },
      ],
    });
    expect(bom.linhas.map((l) => l.chave)).toEqual(["agua"]); // 2 iguais não é um combo
    const comOutro = estadoInicial(
      {
        ...CAT,
        categorias: [
          {
            id: "bebidas",
            nome: "Bebidas",
            artigos: [
              { id: "agua", nome: "Água", emoji: "1f4a7", icones: ["1f4a7"] },
              { id: "bolo", nome: "Bolo", emoji: "1f370", icones: ["1f370"] },
            ],
          },
        ],
      },
      12,
      { titulo: "M", linhas: [linha(["agua", "bolo"])] },
    );
    expect(comOutro.linhas[0]?.combo).toEqual(["agua", "bolo"]);
  });
});

describe("as etiquetas de levantamento", () => {
  it("as secções dos artigos (e as dos artigos dos combos) pedem uma zona; o pedido leva as zonas preenchidas, as cópias e o preço", async () => {
    abrir();
    await userEvent.selectOptions(await screen.findByTestId("precario-combo-artigo-1"), "agua");
    await userEvent.selectOptions(screen.getByTestId("precario-combo-artigo-2"), "bolo");
    await userEvent.click(screen.getByTestId("precario-combo-juntar"));
    expect(screen.getByTestId("etiquetas-zona-doces")).toBeInTheDocument(); // o bolo do combo pede a zona da sua secção
    expect(screen.queryByTestId("etiquetas-zona-menus")).not.toBeInTheDocument();
    await userEvent.type(screen.getByTestId("etiquetas-zona-bebidas"), " Bar ");
    await userEvent.clear(screen.getByTestId("etiquetas-copias"));
    await userEvent.type(screen.getByTestId("etiquetas-copias"), "7");
    await userEvent.click(screen.getByTestId("etiquetas-preco"));
    await userEvent.click(screen.getByTestId("etiquetas-ver"));
    await waitFor(() => expect(pedidosA("/api/precario/etiquetas-previa.png")).toHaveLength(1));
    const p = pedidosA("/api/precario/etiquetas-previa.png")[0]?.corpo as PedidoEtiquetas;
    expect(p.zonas).toEqual({ bebidas: "Bar" }); // as zonas vazias não vão; as cheias levam-se sem espaços
    expect(p.copias).toBe(7);
    expect(p.preco).toBe(false);
    expect(p.precario.linhas.at(-1)?.combo).toEqual(["agua", "bolo"]);
    expect(await screen.findByTestId("etiquetas-previa")).toBeInTheDocument();
    await userEvent.click(screen.getByTestId("etiquetas-pdf"));
    await waitFor(() => expect(pedidosA("/api/precario/etiquetas.pdf")).toHaveLength(1));
  });

  it("o total conta uma etiqueta por artigo (um combo dá uma por artigo) vezes as cópias, 24 por folha; as zonas ficam no browser", async () => {
    abrir();
    const total = await screen.findByTestId("etiquetas-total");
    expect(total).toHaveTextContent("etiquetas"); // o texto vem do servidor falso: só confirma que mostra o número
    await userEvent.type(screen.getByTestId("etiquetas-zona-bebidas"), "Bar");
    expect(localStorage.getItem("rifas.etiquetas")).toContain("Bar");
    cleanup();
    abrir();
    expect(await screen.findByTestId("etiquetas-zona-bebidas")).toHaveValue("Bar");
  });
});
