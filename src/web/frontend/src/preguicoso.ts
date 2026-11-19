import { type ComponentType, lazy } from "react";

// Páginas que só alguns visitantes abrem (o painel do dono, o editor de templates, o sorteio) carregam-se à parte, quando se vai a elas:
// quem só gera rifas não descarrega o código delas. Cada uma é um ficheiro `.js` em `dist/assets` (o `index.html` liga só o principal).
//
// Depois de uma atualização do site os ficheiros com o nome antigo deixam de existir: um separador que já estava aberto falha ao carregar a
// página e, em vez de ficar partido, recarrega-se UMA vez (para trazer os ficheiros novos). A marca vive na sessão do separador e apaga-se
// quando um carregamento corre bem, por isso não há ciclos.

const MARCA = "rifas.recarregou";

// biome-ignore lint/suspicious/noExplicitAny: aceita qualquer componente (cada página tem as suas propriedades)
export function preguicoso<T extends ComponentType<any>>(carregar: () => Promise<{ default: T }>) {
  return lazy(async () => {
    try {
      const modulo = await carregar();
      try {
        sessionStorage.removeItem(MARCA);
      } catch {
        /* sem armazenamento */
      }
      return modulo;
    } catch (erro) {
      let jaRecarregou = true;
      try {
        jaRecarregou = sessionStorage.getItem(MARCA) !== null;
        if (!jaRecarregou) sessionStorage.setItem(MARCA, "1");
      } catch {
        /* sem armazenamento: não se recarrega (para não haver ciclos) */
      }
      if (jaRecarregou) throw erro;
      window.location.reload();
      return new Promise<{ default: T }>(() => {}); // a página vai recarregar: nada a mostrar entretanto
    }
  });
}
