import { StrictMode } from "react";
import "@fontsource-variable/bricolage-grotesque";
import "@fontsource-variable/fraunces";
import "@fontsource-variable/fredoka";
import "@fontsource-variable/jetbrains-mono";
import "@fontsource-variable/jost";
import "@fontsource-variable/orbitron";
import "@fontsource-variable/pixelify-sans";
import "@fontsource-variable/playfair-display";
import "@fontsource-variable/source-serif-4";
import "@fontsource-variable/space-grotesk";
import "@fontsource/alfa-slab-one";
import "@fontsource/creepster";
import "@fontsource/marcellus";
import "@fontsource/rye";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { ProvedorI18n } from "./i18n";
import "./estilos/main.scss";

const raiz = document.getElementById("raiz");
if (!raiz) throw new Error("falta #raiz");
createRoot(raiz).render(
  <StrictMode>
    <ProvedorI18n>
      <App />
    </ProvedorI18n>
  </StrictMode>,
);
