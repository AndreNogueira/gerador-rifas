// A foto própria de um artigo do preçário: só PNG ou JPG, reduzida aqui no browser (lado máximo 192 px, o que o servidor também usa) para não enviar fotografias
// inteiras. Nada se guarda: a foto vai no pedido que desenha a pré-visualização e o PDF, e fica só no estado da página (nem no rascunho do browser).
export const FOTO_LADO = 192;
export const LOGO_LADO = 480;
const TIPOS = ["image/png", "image/jpeg"];
const MAX_ORIGINAL = 12 * 1024 * 1024;

export async function prepararFoto(ficheiro: File, lado = FOTO_LADO): Promise<string> {
  if (!TIPOS.includes(ficheiro.type) || ficheiro.size > MAX_ORIGINAL) throw new Error("tipo");
  const bitmap = await createImageBitmap(ficheiro);
  try {
    const k = Math.min(1, lado / Math.max(bitmap.width, bitmap.height));
    const tela = document.createElement("canvas");
    tela.width = Math.max(1, Math.round(bitmap.width * k));
    tela.height = Math.max(1, Math.round(bitmap.height * k));
    const ctx = tela.getContext("2d");
    if (!ctx) throw new Error("canvas");
    ctx.drawImage(bitmap, 0, 0, tela.width, tela.height);
    return tela.toDataURL(ficheiro.type === "image/png" ? "image/png" : "image/jpeg", 0.85);
  } finally {
    bitmap.close();
  }
}
