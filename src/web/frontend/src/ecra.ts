// Diz ao servidor, UMA vez por separador, que tipo de ecra e de aparelho visita o site (so para as estatisticas do painel do dono:
// nunca muda o que se ve). Vai o tamanho do ecra e da janela, a densidade de pixeis, se ha toque e, nos Chrome que o dizem, o modelo
// do telemovel. O servidor guarda so a classe (telemovel, tablet, computador...) e esses tamanhos: sem IP, sem User-Agent.

type NavegadorComModelo = Navigator & {
  userAgentData?: { getHighEntropyValues(dicas: string[]): Promise<{ model?: string }> };
};

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
      }),
      keepalive: true,
    });
  } catch {
    /* as estatísticas nunca incomodam o utilizador */
  }
}
