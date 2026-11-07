/**
 * Os temas visuais («estilos») da webapp. Um tema é uma folha `temas/<id>.css` que reescreve as variáveis de `estilos.css`
 * (ver `docs/TEMAS.md`); aqui só se regista o nome. Os nomes são próprios (não se traduzem). Cada tema tem claro e escuro.
 */
export const VISUAIS = [
  {
    id: "premiado",
    nome: "Premiado",
    descricao: "O bilhete premiado: violeta e magenta, picotado e entalhes.",
  },
  {
    id: "quermesse",
    nome: "Quermesse",
    descricao: "Feira popular: toldo às riscas, lâmpadas e bilhetes de papel.",
  },
  { id: "arcade", nome: "Arcade", descricao: "Pixéis e néon, como um ecrã de máquina de jogos." },
  { id: "brutalista", nome: "Brutalista", descricao: "Contornos grossos, sombras duras e cores chapadas." },
  { id: "risografia", nome: "Risografia", descricao: "Impressão de duas tintas sobre papel, com retícula." },
  { id: "janela98", nome: "Janela 98", descricao: "Cada passo é uma janela de um computador dos anos 90." },
  { id: "gala", nome: "Gala", descricao: "Art déco: dourado sobre azul-noite, para a rifa de gala." },
  { id: "natal", nome: "Natal", descricao: "A rifa de Natal: verde, vermelho, dourado e neve a cair." },
] as const;

export type Visual = (typeof VISUAIS)[number]["id"];
export const VISUAL_POR_OMISSAO: Visual = "premiado";

export function visualValido(v: string | null | undefined): v is Visual {
  return VISUAIS.some((x) => x.id === v);
}
