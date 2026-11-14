// Prepara a imagem (o logótipo) que se junta ao desenho do editor: só PNG ou JPG, reduzida no browser (lado máximo 600 px) para não enviar fotografias
// inteiras. O servidor volta a validar o tipo real e recodifica (core.editor._imagem); isto só poupa largura de banda e dá logo uma mensagem.
import { LIMITES } from "./editor-modelo";

export interface ImagemPronta {
  dados: string;
  largura: number;
  altura: number;
}

const TIPOS = ["image/png", "image/jpeg"];
const MAX_ORIGINAL = 12 * 1024 * 1024;

const bytesDe = (dataUrl: string) => Math.floor(((dataUrl.length - dataUrl.indexOf(",") - 1) * 3) / 4);

export async function prepararImagem(ficheiro: File): Promise<ImagemPronta> {
  if (!TIPOS.includes(ficheiro.type) || ficheiro.size > MAX_ORIGINAL) throw new Error("tipo");
  const bitmap = await createImageBitmap(ficheiro);
  try {
    const k = Math.min(1, LIMITES.imagemLado / Math.max(bitmap.width, bitmap.height));
    const largura = Math.max(1, Math.round(bitmap.width * k));
    const altura = Math.max(1, Math.round(bitmap.height * k));
    const tela = document.createElement("canvas");
    tela.width = largura;
    tela.height = altura;
    const ctx = tela.getContext("2d");
    if (!ctx) throw new Error("canvas");
    ctx.drawImage(bitmap, 0, 0, largura, altura);
    let dados = tela.toDataURL(ficheiro.type === "image/png" ? "image/png" : "image/jpeg", 0.88);
    if (bytesDe(dados) > LIMITES.imagemBytes) dados = tela.toDataURL("image/jpeg", 0.7); // um PNG grande: passa a JPG (sem transparência)
    if (bytesDe(dados) > LIMITES.imagemBytes) throw new Error("tamanho");
    return { dados, largura, altura };
  } finally {
    bitmap.close();
  }
}
