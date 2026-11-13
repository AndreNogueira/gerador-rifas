import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ProvedorDialogos } from "./dialogos";
import { ProvedorI18n } from "./i18n";
import { enderecoParaPartilhar, ligacoesDePartilha, Partilhar } from "./Partilhar";
import { ServidorFalso } from "./servidor-falso";

beforeEach(() => {
  localStorage.clear();
  new ServidorFalso().instalar();
});

async function abrir(variante: "rodape" | "cartao" = "rodape") {
  render(
    <ProvedorI18n>
      <ProvedorDialogos>
        <Partilhar variante={variante} />
      </ProvedorDialogos>
    </ProvedorI18n>,
  );
  await screen.findByText("Partilhar"); // os textos chegam do servidor
}

describe("endereços e ligações de partilha", () => {
  it("o endereço leva a língua do URL; o português fica em /", () => {
    expect(enderecoParaPartilhar("https://rifas.pt", "pt")).toBe("https://rifas.pt/");
    expect(enderecoParaPartilhar("https://rifas.pt", null)).toBe("https://rifas.pt/");
    expect(enderecoParaPartilhar("https://rifas.pt", "en")).toBe("https://rifas.pt/en");
    expect(enderecoParaPartilhar("https://rifas.pt", "ja")).toBe("https://rifas.pt/ja");
  });

  it("as ligações são simples (https ou mailto), levam o texto e o endereço bem codificados e nenhum rastreio", () => {
    const l = ligacoesDePartilha("https://rifas.pt/en", "Rifas & mais: grátis", "Gerador de Rifas");
    expect(l.map((x) => x.id)).toEqual(["whatsapp", "telegram", "facebook", "email"]);
    expect(l[0]?.href).toBe(
      `https://wa.me/?text=${encodeURIComponent("Rifas & mais: grátis https://rifas.pt/en")}`,
    );
    expect(l[2]?.href).toBe(
      `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent("https://rifas.pt/en")}`,
    );
    expect(l[3]?.href.startsWith("mailto:?subject=Gerador%20de%20Rifas&body=")).toBe(true);
    for (const x of l) expect(x.href).not.toMatch(/utm_|fbclid|track|pixel/i);
  });
});

describe("o botão Partilhar", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    Object.defineProperty(navigator, "share", { value: undefined, configurable: true });
  });

  it("começa fechado e abre a lista com WhatsApp, Telegram, Facebook, e-mail e copiar", async () => {
    await abrir();
    expect(screen.queryByRole("list", { name: "Partilhar" })).not.toBeInTheDocument();
    const botao = screen.getByTestId("partilhar-abrir-rodape");
    expect(botao).toHaveAttribute("aria-expanded", "false");
    await userEvent.click(botao);
    expect(botao).toHaveAttribute("aria-expanded", "true");
    const lista = screen.getByRole("list", { name: "Partilhar" });
    for (const id of ["whatsapp", "telegram", "facebook", "email"])
      expect(within(lista).getByTestId(`partilhar-${id}`)).toBeInTheDocument();
    const wa = within(lista).getByTestId("partilhar-whatsapp");
    expect(wa).toHaveAttribute("target", "_blank");
    expect(wa).toHaveAttribute("rel", "noopener noreferrer");
    expect(wa.getAttribute("href")).toContain(encodeURIComponent(`${window.location.origin}/`));
    expect(within(lista).queryByTestId("partilhar-nativa")).not.toBeInTheDocument();
  });

  it("copiar põe o endereço na área de transferência e avisa", async () => {
    const escrever = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", { value: { writeText: escrever }, configurable: true });
    await abrir();
    await userEvent.click(screen.getByTestId("partilhar-abrir-rodape"));
    await userEvent.click(screen.getByTestId("partilhar-copiar"));
    expect(escrever).toHaveBeenCalledWith(`${window.location.origin}/`);
    expect(await screen.findByText("Ligação copiada.")).toBeInTheDocument();
  });

  it("com a partilha nativa do browser, oferece-a primeiro e usa-a", async () => {
    const partilhar = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "share", { value: partilhar, configurable: true });
    await abrir();
    await userEvent.click(screen.getByTestId("partilhar-abrir-rodape"));
    await userEvent.click(screen.getByTestId("partilhar-nativa"));
    expect(partilhar).toHaveBeenCalledWith(expect.objectContaining({ url: `${window.location.origin}/` }));
  });

  it("no cartão dos ficheiros convida a partilhar", async () => {
    await abrir("cartao");
    expect(screen.getByText("Gostou? Partilhe com quem também faz rifas.")).toBeInTheDocument();
  });
});
