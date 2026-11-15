import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { Donativo } from "./Donativo";
import { ProvedorI18n } from "./i18n";
import { ServidorFalso } from "./servidor-falso";

beforeEach(() => {
  localStorage.clear();
  new ServidorFalso().instalar();
});

function mostrar(url: string, variante: "topo" | "cartao") {
  return render(
    <ProvedorI18n>
      <Donativo url={url} variante={variante} />
    </ProvedorI18n>,
  );
}

describe("o botão Donativo", () => {
  it("sem DONATIVO_URL não aparece nada", () => {
    mostrar("", "topo");
    mostrar("", "cartao");
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
    expect(screen.queryByText(/gratuito/)).not.toBeInTheDocument();
  });

  it("no cabeçalho é uma ligação com o texto, que abre noutro separador sem referrer", async () => {
    mostrar("https://exemplo.pt/doar", "topo");
    const ligacao = await screen.findByTestId("donativo-topo");
    expect(ligacao).toHaveAttribute("href", "https://exemplo.pt/doar");
    expect(ligacao).toHaveAttribute("target", "_blank");
    expect(ligacao).toHaveAttribute("rel", "noopener noreferrer");
    expect(ligacao).toHaveTextContent("Donativo");
  });

  it("depois de gerar, o cartão traz a frase de convite e a ligação", async () => {
    mostrar("https://exemplo.pt/doar", "cartao");
    expect(await screen.findByText(/manter o serviço gratuito/)).toBeInTheDocument();
    expect(screen.getByTestId("donativo-cartao")).toHaveAttribute("href", "https://exemplo.pt/doar");
  });
});
