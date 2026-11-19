import { render, screen } from "@testing-library/react";
import { Component, type ReactNode, Suspense } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { preguicoso } from "./preguicoso";

const recarregar = vi.fn();

class Limite extends Component<{ children: ReactNode }, { erro: boolean }> {
  state = { erro: false };
  static getDerivedStateFromError() {
    return { erro: true };
  }
  render() {
    return this.state.erro ? <p>falhou mesmo</p> : this.props.children;
  }
}

beforeEach(() => {
  sessionStorage.clear();
  recarregar.mockClear();
  vi.stubGlobal("location", { ...window.location, reload: recarregar });
});
afterEach(() => vi.unstubAllGlobals());

function Pagina() {
  return <p>conteúdo da página</p>;
}

describe("as páginas carregadas à parte", () => {
  it("mostram o conteúdo quando o ficheiro chega e limpam a marca de recarga", async () => {
    sessionStorage.setItem("rifas.recarregou", "1");
    const Preguicosa = preguicoso(() => Promise.resolve({ default: Pagina }));
    render(
      <Suspense fallback={<p>a carregar</p>}>
        <Preguicosa />
      </Suspense>,
    );
    expect(await screen.findByText("conteúdo da página")).toBeInTheDocument();
    expect(sessionStorage.getItem("rifas.recarregou")).toBeNull();
    expect(recarregar).not.toHaveBeenCalled();
  });

  it("se o ficheiro já não existe (o site foi atualizado) recarrega a página UMA vez", async () => {
    const Preguicosa = preguicoso(() =>
      Promise.reject(new Error("Failed to fetch dynamically imported module")),
    );
    render(
      <Suspense fallback={<p>a carregar</p>}>
        <Preguicosa />
      </Suspense>,
    );
    await vi.waitFor(() => expect(recarregar).toHaveBeenCalledTimes(1));
    expect(sessionStorage.getItem("rifas.recarregou")).toBe("1");
    expect(screen.getByText("a carregar")).toBeInTheDocument(); // entretanto nada de partido: a página vai recarregar
  });

  it("se voltar a falhar depois de recarregar não entra em ciclo: deixa o erro aparecer", async () => {
    sessionStorage.setItem("rifas.recarregou", "1");
    const erro = vi.spyOn(console, "error").mockImplementation(() => {});
    const Preguicosa = preguicoso(() => Promise.reject(new Error("sem rede")));

    render(
      <Limite>
        <Suspense fallback={<p>a carregar</p>}>
          <Preguicosa />
        </Suspense>
      </Limite>,
    );
    expect(await screen.findByText("falhou mesmo")).toBeInTheDocument();
    expect(recarregar).not.toHaveBeenCalled();
    erro.mockRestore();
  });
});
