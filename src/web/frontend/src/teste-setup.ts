import "@testing-library/jest-dom/vitest";
import { configure } from "@testing-library/react";
import { beforeEach } from "vitest";

// dentro do Docker (o CI constrói a imagem com os testes lá dentro) a máquina está carregada e 1 s não chega para a página aparecer
configure({ asyncUtilTimeout: 5000 });

// o endereço do jsdom persiste entre testes do mesmo ficheiro: sem isto, uma língua escolhida num teste (`/en`) mandava no seguinte
beforeEach(() => window.history.replaceState(null, "", "/"));
