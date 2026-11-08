import "@testing-library/jest-dom/vitest";
import { beforeEach } from "vitest";

// o endereço do jsdom persiste entre testes do mesmo ficheiro: sem isto, uma língua escolhida num teste (`/en`) mandava no seguinte
beforeEach(() => window.history.replaceState(null, "", "/"));
