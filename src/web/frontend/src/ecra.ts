// Diz ao servidor, UMA vez por separador, que tipo de ecra e de aparelho visita o site (so para as estatisticas do painel do dono:
// nunca muda o que se ve). Vai o tamanho do ecra e da janela, a densidade de pixeis, se ha toque e, nos Chrome que o dizem, o modelo
// do telemovel, e de onde veio a visita: SO o nome do servidor de onde chegou (nunca o endereco completo) e o `utm_source` do endereco, se tiver. O
// servidor guarda so a classe (telemovel, tablet, computador...), esses tamanhos e a CATEGORIA da origem (pesquisa, rede social...): sem IP, sem User-Agent.

type NavegadorComModelo = Navigator & {
  userAgentData?: { getHighEntropyValues(dicas: string[]): Promise<{ model?: string }> };
};

/** O nome do servidor de onde o visitante veio, ou vazio (nunca o caminho nem os parametros do endereco de origem). */
export function origemDaVisita(referrer: string = document.referrer): string {
  try {
    return referrer ? new URL(referrer).hostname.slice(0, 253) : "";
  } catch {
    return "";
  }
}

/** O `utm_source` do endereco atual (o nome de uma campanha), ou vazio. */
export function campanhaDaVisita(pesquisa: string = window.location.search): string {
  try {
    return (new URLSearchParams(pesquisa).get("utm_source") ?? "").slice(0, 40);
  } catch {
    return "";
  }
}

export async function registarEcra(): Promise<void> {
  try {
    if (!screen.width || !screen.height || sessionStorage.getItem("rifas.ecra")) return;
    sessionStorage.setItem("rifas.ecra", "1");
  } catch {
    return; // sem armazenamento: não se regista (para não repetir a cada página)
  }
  let modelo = "";
  try {
    modelo =
      (await (navigator as NavegadorComModelo).userAgentData?.getHighEntropyValues(["model"]))?.model ?? "";
  } catch {
    /* o browser não diz o modelo */
  }
  try {
    await fetch("/api/ecra", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ecra_l: screen.width,
        ecra_a: screen.height,
        janela_l: window.innerWidth,
        janela_a: window.innerHeight,
        dpr: window.devicePixelRatio || 1,
        toque: navigator.maxTouchPoints > 0,
        modelo,
        origem: origemDaVisita(),
        campanha: campanhaDaVisita(),
      }),
      keepalive: true,
    });
  } catch {
    /* as estatísticas nunca incomodam o utilizador */
  }
}
