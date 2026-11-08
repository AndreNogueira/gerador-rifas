import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it } from "vitest";
import {
  comPrefixo,
  definirLinguaDaRota,
  Ligacao,
  linguaDoCaminho,
  semPrefixo,
  useLocalizacao,
} from "./rota";

describe("o prefixo da língua no URL", () => {
  it("tira e põe o prefixo, com a query e sem tocar no português nem no painel", () => {
    expect(semPrefixo("/en/tutorial")).toBe("/tutorial");
    expect(semPrefixo("/en")).toBe("/");
    expect(semPrefixo("/tutorial")).toBe("/tutorial");
    expect(semPrefixo("/entrar")).toBe("/entrar"); // «en» só conta como segmento inteiro
    expect(linguaDoCaminho("/ja/sorteio")).toBe("ja");
    expect(linguaDoCaminho("/sorteio")).toBeNull();
    expect(comPrefixo("/tutorial?p=3", "en")).toBe("/en/tutorial?p=3");
    expect(comPrefixo("/", "ja")).toBe("/ja");
    expect(comPrefixo("/?a=1", "ja")).toBe("/ja?a=1");
    expect(comPrefixo("/tutorial", "pt")).toBe("/tutorial");
    expect(comPrefixo("/tutorial", null)).toBe("/tutorial");
    expect(comPrefixo("/admin", "en")).toBe("/admin");
    expect(comPrefixo("/tutorial", "klingon")).toBe("/tutorial");
  });
});

function Aqui() {
  return <output data-testid="aqui">{useLocalizacao()}</output>;
}

describe("Ligacao e useLocalizacao com língua", () => {
  afterEach(() => definirLinguaDaRota("pt"));

  it("o href leva o prefixo da língua, o clique navega para ele e a localização de dentro continua sem prefixo", async () => {
    act(() => definirLinguaDaRota("de"));
    render(
      <>
        <Ligacao para="/tutorial">ir</Ligacao>
        <Aqui />
      </>,
    );
    expect(screen.getByText("ir")).toHaveAttribute("href", "/de/tutorial");
    await userEvent.click(screen.getByText("ir"));
    expect(window.location.pathname).toBe("/de/tutorial");
    expect(screen.getByTestId("aqui")).toHaveTextContent("/tutorial");
    act(() => definirLinguaDaRota("pt"));
    expect(window.location.pathname).toBe("/tutorial");
    expect(screen.getByText("ir")).toHaveAttribute("href", "/tutorial");
  });
});
