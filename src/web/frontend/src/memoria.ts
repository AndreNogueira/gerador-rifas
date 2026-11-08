// A memória do browser (IndexedDB): lembra o ficheiro dos algarismos da última vez, para quem volta todos os anos não o repetir.
// Nada vai para o servidor: o ficheiro só é enviado, como sempre, quando se começa uma sessão e ainda não há algarismos.
// «Limpar tudo» apaga-o. Sem IndexedDB (navegação privada, bloqueado) tudo isto fica em silêncio: o resto da app não muda.
const BASE = "rifas";
const LOJA = "ficheiros";
const CHAVE = "algarismos";
const MAX_BYTES = 10 * 1024 * 1024; // acima disto não se guarda (o limite do servidor é maior; aqui basta o que uma letra ocupa)

interface Guardado {
  nome: string;
  tipo: string;
  dados: ArrayBuffer;
}

function abrir(): Promise<IDBDatabase | null> {
  return new Promise((resolver) => {
    try {
      if (typeof indexedDB === "undefined") return resolver(null);
      const pedido = indexedDB.open(BASE, 1);
      pedido.onupgradeneeded = () => pedido.result.createObjectStore(LOJA);
      pedido.onsuccess = () => resolver(pedido.result);
      pedido.onerror = () => resolver(null);
      pedido.onblocked = () => resolver(null);
    } catch {
      resolver(null);
    }
  });
}

async function usar<T>(
  modo: IDBTransactionMode,
  fazer: (loja: IDBObjectStore) => IDBRequest<T>,
): Promise<T | null> {
  const bd = await abrir();
  if (!bd) return null;
  try {
    return await new Promise<T | null>((resolver) => {
      const pedido = fazer(bd.transaction(LOJA, modo).objectStore(LOJA));
      pedido.onsuccess = () => resolver(pedido.result);
      pedido.onerror = () => resolver(null);
    });
  } catch {
    return null;
  } finally {
    bd.close();
  }
}

/** Guarda (ou troca) o ficheiro dos algarismos. Devolve false se não coube ou não houve onde guardar. */
export async function guardarAlgarismos(ficheiro: File): Promise<boolean> {
  if (ficheiro.size > MAX_BYTES) return false;
  const dados = await ficheiro.arrayBuffer();
  const guardado: Guardado = { nome: ficheiro.name, tipo: ficheiro.type, dados };
  return (await usar("readwrite", (l) => l.put(guardado, CHAVE))) !== null;
}

/** O ficheiro dos algarismos da última vez, ou null. */
export async function lerAlgarismos(): Promise<File | null> {
  const g = await usar<Guardado | undefined>(
    "readonly",
    (l) => l.get(CHAVE) as IDBRequest<Guardado | undefined>,
  );
  if (!g || typeof g.nome !== "string" || Object.prototype.toString.call(g.dados) !== "[object ArrayBuffer]")
    return null; // sem instanceof: o ArrayBuffer pode vir de outro contexto (testes)
  return new File([g.dados], g.nome, { type: g.tipo });
}

export async function esquecerAlgarismos(): Promise<void> {
  await usar("readwrite", (l) => l.delete(CHAVE));
}
