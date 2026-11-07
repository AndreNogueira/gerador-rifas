import { StrictMode } from "react";
import "@fontsource-variable/bricolage-grotesque";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { ProvedorI18n } from "./i18n";
import "./estilos.css";

const raiz = document.getElementById("raiz");
if (!raiz) throw new Error("falta #raiz");
createRoot(raiz).render(
  <StrictMode>
    <ProvedorI18n>
      <App />
    </ProvedorI18n>
  </StrictMode>,
);
