import { join } from "node:path";

/** Os ficheiros de exemplo de `tests/fixtures` (na raiz do repositório). */
export const fixture = (nome: string) =>
  join(import.meta.dirname, "..", "..", "..", "..", "tests", "fixtures", nome);
