import { type FormEvent, type ReactNode, useCallback, useEffect, useState } from "react";
import { AdminErros } from "./AdminErros";
import { AdminSeo } from "./AdminSeo";
import {
  adminApi,
  type Contagem,
  type Dados,
  ErroEntrada,
  type Estado,
  NaoAutenticado,
  type VeredictoProxy,
} from "./admin-api";
import {
  BarrasH,
  CORES,
  Funil,
  formatarNumero,
  GraficoBarras,
  GraficoLinhas,
  Medidor,
  Rosca,
} from "./graficos";
import { Icone } from "./icones";

/*
 * O painel de administração (`/admin`). Só existe se o servidor tiver `ADMIN_TOKEN`; sem sessão pede a palavra-passe.
 * EXCEÇÃO DELIBERADA: os textos estão só em português (é um painel do dono, não da interface pública das 18 línguas).
 */

const JANELAS: Record<string, number> = {
  "1h": 3600,
  "6h": 21600,
  "24h": 86400,
  "7d": 604800,
  "30d": 2592000,
};
const ROTULO_INTERVALO: Record<string, string> = {
  "1h": "Última hora",
  "6h": "Últimas 6 horas",
  "24h": "Últimas 24 horas",
  "7d": "Últimos 7 dias",
  "30d": "Últimos 30 dias",
};

const dataHora = (t: number) =>
  new Date(t * 1000).toLocaleString("pt-PT", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });

/** O servidor só guarda o código do país (ISO, duas letras; `??` = desconhecido): o nome em português escreve-se aqui, com o código à frente (as bandeiras em emoji não aparecem no Windows). */
export function nomesDosPaises(itens: Contagem[]): Contagem[] {
  let nomes: Intl.DisplayNames | null = null;
  try {
    nomes = new Intl.DisplayNames(["pt-PT"], { type: "region" });
  } catch {
    /* sem suporte: fica o código */
  }
  return itens.map((i) => {
    if (!/^[A-Z]{2}$/.test(i.chave)) return { ...i, chave: "Desconhecido" };
    let nome = "";
    try {
      nome = nomes?.of(i.chave) ?? "";
    } catch {
      /* código sem nome */
    }
    return { ...i, chave: nome && nome !== i.chave ? `${nome} (${i.chave})` : i.chave };
  });
}

function duracao(s: number | null): string {
  if (s === null) return "—";
  if (s < 10) return `${s.toFixed(1)} s`;
  if (s < 90) return `${Math.round(s)} s`;
  if (s < 5400) return `${Math.round(s / 60)} min`;
  const h = Math.floor(s / 3600);
  return h < 48 ? `${h} h ${Math.round((s % 3600) / 60)} min` : `${Math.round(s / 86400)} dias`;
}

function Seccao({
  id,
  titulo,
  explica,
  children,
}: {
  id: string;
  titulo: string;
  explica?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="cartao admin-seccao" aria-labelledby={id}>
      <h2 id={id}>{titulo}</h2>
      {explica && <p className="explica">{explica}</p>}
      {children}
    </section>
  );
}

function Numero({
  rotulo,
  valor,
  sub,
  explica,
  alerta,
}: {
  rotulo: string;
  valor: string;
  sub?: string;
  explica: string;
  alerta?: boolean;
}) {
  return (
    <div className={`stat${alerta ? " alerta" : ""}`}>
      <span className="rotulo">{rotulo}</span>
      <span className="valor">{valor}</span>
      {sub && <span className="sub">{sub}</span>}
      <p className="explica">{explica}</p>
    </div>
  );
}

function Grafico({ titulo, como, children }: { titulo: string; como: string; children: ReactNode }) {
  return (
    <div className="grafico-bloco">
      <h3>{titulo}</h3>
      {children}
      <p className="explica">
        <b>Como ler:</b> {como}
      </p>
    </div>
  );
}

function Entrar({ aoEntrar }: { aoEntrar: () => void }) {
  const [token, setToken] = useState("");
  const [erro, setErro] = useState("");
  const [a_enviar, setAEnviar] = useState(false);

  async function enviar(e: FormEvent) {
    e.preventDefault();
    setAEnviar(true);
    setErro("");
    try {
      await adminApi.entrar(token);
      setToken(""); // a palavra-passe não fica em memória depois de entrar
      aoEntrar();
    } catch (x) {
      setErro(x instanceof ErroEntrada ? x.message : "Sem ligação ao servidor.");
    } finally {
      setAEnviar(false);
    }
  }

  return (
    <section className="cartao admin-entrar" aria-labelledby="admin-entrar-t">
      <h2 id="admin-entrar-t">Entrar no painel</h2>
      <form onSubmit={enviar}>
        <label>
          Palavra-passe
          <input
            type="password"
            autoComplete="current-password"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            data-testid="admin-token"
            required
          />
        </label>
        {erro && (
          <p role="alert" className="cor-erro" data-testid="admin-erro">
            {erro}
          </p>
        )}
        <button type="submit" disabled={a_enviar || !token} data-testid="admin-entrar">
          <Icone nome="verificado" />
          Entrar
        </button>
        <p className="explica">
          É a variável <code>ADMIN_TOKEN</code> do serviço (no Render, em Environment). Não é a de nenhuma
          conta.
        </p>
      </form>
    </section>
  );
}

const MENSAGEM_PROXY: Record<VeredictoProxy, { cor: string; texto: string }> = {
  sem_dados: { cor: "suave", texto: "Ainda não chegaram pedidos para avaliar." },
  poucos_pedidos: {
    cor: "suave",
    texto: "Ainda há poucos pedidos (são precisos uns 20 na última hora) para tirar conclusões.",
  },
  sem_proxy: {
    cor: "ok",
    texto:
      "Não há proxy à frente do servidor (é o normal no teu computador): o IP que o servidor vê é o do cliente.",
  },
  ok: {
    cor: "ok",
    texto: "Os IPs reais dos visitantes chegam ao servidor: o limite de pedidos por IP funciona por pessoa.",
  },
  problema: {
    cor: "erro",
    texto:
      "ATENÇÃO: quase todos os pedidos aparecem como vindos de 1 ou 2 endereços internos, apesar de trazerem X-Forwarded-For. O servidor não confia no proxy, por isso o limite por IP é, na prática, global (uma pessoa pode esgotá-lo para todos). Define FORWARDED_ALLOW_IPS=* no serviço (o Render é o único caminho até ao contentor).",
  },
};

const LIMITES: [string, string, string][] = [
  ["max_numeros", "Números por pedido", ""],
  ["max_upload_mb", "Tamanho de cada ficheiro", " MB"],
  ["max_sessoes", "Sessões em simultâneo", ""],
  ["validade_min", "Ficheiros apagados após inatividade de", " min"],
  ["tempo_maximo_geracao_min", "Tempo máximo de uma geração", " min"],
  ["pedidos_pesados_por_min", "Uploads, pré-visualizações e gerações por minuto e por IP", ""],
  ["pedidos_leves_por_min", "Outros pedidos por minuto e por IP", ""],
  ["forwarded_allow_ips", "Proxies em que se confia (X-Forwarded-For)", ""],
];

export function Admin() {
  const [estado, setEstado] = useState<Estado | null>(null);
  const [dados, setDados] = useState<Dados | null>(null);
  const [intervalo, setIntervalo] = useState("6h");
  const [fase, setFase] = useState<"a_ver" | "entrar" | "dentro">("a_ver");
  const [falha, setFalha] = useState("");

  const carregarEstado = useCallback(async () => {
    try {
      setEstado(await adminApi.estado());
      setFase("dentro");
      setFalha("");
    } catch (e) {
      if (e instanceof NaoAutenticado) {
        setEstado(null);
        setDados(null);
        setFase("entrar");
      } else setFalha("Não foi possível atualizar (o servidor pode estar a reiniciar).");
    }
  }, []);

  const carregarDados = useCallback(async () => {
    try {
      setDados(await adminApi.dados(intervalo));
    } catch (e) {
      if (e instanceof NaoAutenticado) setFase("entrar");
    }
  }, [intervalo]);

  useEffect(() => {
    void carregarEstado();
  }, [carregarEstado]);

  useEffect(() => {
    if (fase !== "dentro") return;
    const a = setInterval(() => void carregarEstado(), 10000);
    return () => clearInterval(a);
  }, [fase, carregarEstado]);

  useEffect(() => {
    if (fase !== "dentro") return;
    void carregarDados();
    const a = setInterval(() => void carregarDados(), 30000);
    return () => clearInterval(a);
  }, [fase, carregarDados]);

  if (fase === "a_ver")
    return (
      <div className="pagina admin">
        <h1>Painel</h1>
        <p aria-busy="true">…</p>
      </div>
    );
  if (fase === "entrar")
    return (
      <div className="pagina admin">
        <h1>Painel</h1>
        <Entrar aoEntrar={() => void carregarEstado()} />
      </div>
    );
  if (!estado) return null;

  const sis = estado.sistema;
  const ate = dados ? dados.desde + (JANELAS[dados.intervalo] ?? 0) : estado.agora;
  const desde = dados?.desde ?? estado.agora - (JANELAS[intervalo] ?? 0);
  const passo = dados?.passo_s ?? 60;
  const r = dados?.resumo;
  const serie = <K extends string>(linhas: ({ t: number } & Record<K, number | null>)[] | undefined, k: K) =>
    (linhas ?? []).map((p) => ({ t: p.t, v: p[k] }));
  const geracoesTotal = r ? Object.values(r.geracoes).reduce((a, b) => a + b, 0) : 0;
  const proxy = MENSAGEM_PROXY[estado.proxy.veredicto];

  return (
    <div className="pagina admin">
      <h1>Painel</h1>

      <section className="cartao admin-barra" aria-label="Estado do painel">
        <div className="admin-resumo">
          <span>
            Versão <b>{estado.versao}</b>
          </span>
          {estado.papel === "leitura" && (
            <span role="status" data-testid="admin-so-leitura">
              <b>Só de leitura</b> (não pode mudar nada)
            </span>
          )}
          <span>
            a correr há <b>{duracao(estado.agora - estado.arranque)}</b> (desde {dataHora(estado.arranque)})
          </span>
          <span>
            dados desde <b>{dataHora(estado.dados_desde)}</b>
          </span>
        </div>
        <div className="botoes">
          <label className="seletor-admin">
            <span className="so-leitores">Intervalo</span>
            <select
              value={intervalo}
              onChange={(e) => setIntervalo(e.target.value)}
              data-testid="admin-intervalo"
            >
              {estado.intervalos.map((i) => (
                <option key={i} value={i}>
                  {ROTULO_INTERVALO[i] ?? i}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            className="secundario"
            onClick={() => {
              void carregarEstado();
              void carregarDados();
            }}
          >
            <Icone nome="auto" />
            Atualizar
          </button>
          <button
            type="button"
            className="texto"
            onClick={async () => {
              await adminApi.sair();
              setEstado(null);
              setDados(null);
              setFase("entrar");
            }}
            data-testid="admin-sair"
          >
            <Icone nome="fechar" />
            Sair
          </button>
        </div>
        {estado.dados_efemeros && (
          <p className="aviso-efemero" role="note">
            <b>Os dados são temporários.</b> O plano gratuito do Render apaga o disco quando o serviço
            adormece (15 min sem visitas) ou é atualizado, por isso os gráficos só têm o que aconteceu desde{" "}
            {dataHora(estado.dados_desde)}. Para os guardar é preciso um disco persistente ou uma base de
            dados externa (ver docs/ADMIN.md).
          </p>
        )}
        {estado.base_de_dados.erro && (
          <p role="alert" className="cor-aviso" data-testid="admin-bd-erro">
            <b>A base de dados não responde.</b> As métricas ficam em memória e voltam a ser gravadas assim
            que ela responder (os gráficos podem estar vazios). O gerador continua a funcionar.
          </p>
        )}
        {estado.base_de_dados.tipo === "postgres" && !estado.base_de_dados.erro && (
          <p className="cor-ok" role="note" data-testid="admin-bd-ok">
            Métricas guardadas na base de dados (gravação de {estado.base_de_dados.intervalo_min} em{" "}
            {estado.base_de_dados.intervalo_min} minutos): sobrevivem a reinícios.
          </p>
        )}
        {falha && (
          <p role="alert" className="cor-aviso">
            {falha}
          </p>
        )}
      </section>

      <Seccao
        id="agora"
        titulo="Agora"
        explica="O estado do servidor neste momento (atualiza de 10 em 10 segundos). O Render gratuito dá 512 MB de memória e menos de um núcleo de CPU."
      >
        <div className="stats">
          <Numero
            rotulo="CPU"
            valor={`${sis.cpu.toFixed(0)} %`}
            sub={`de 1 núcleo (a máquina tem ${sis.cpu_nucleos})`}
            alerta={sis.cpu > 90}
            explica="Quanto do processador se está a usar (servidor e motor juntos). Perto de 0 em repouso; sobe a gerar PDFs. Colado nos 100 % durante muito tempo, tudo fica lento."
          />
          <Numero
            rotulo="Memória do servidor"
            valor={`${Math.round(sis.mem_servidor_mb)} MB`}
            explica="O processo que atende os pedidos (a API). Costuma ficar estável e pequeno."
          />
          <Numero
            rotulo="Memória do motor"
            valor={`${Math.round(sis.mem_motor_mb)} MB`}
            explica="O processo à parte que lê os PDFs e gera as rifas. Sobe com ficheiros grandes e volta a descer quando é recriado."
          />
          <Numero
            rotulo="Memória total"
            valor={`${Math.round(sis.mem_contentor_mb)} MB`}
            sub={sis.mem_limite_mb ? `limite ${Math.round(sis.mem_limite_mb)} MB` : "sem limite aqui"}
            alerta={!!sis.mem_limite_mb && sis.mem_contentor_mb / sis.mem_limite_mb > 0.85}
            explica="O que conta para o Render: se passar do limite, o serviço é morto (falta de memória). A vermelho a partir de 85 %."
          />
          <Numero
            rotulo="Disco"
            valor={`${sis.disco_usado_mb.toFixed(1)} MB`}
            sub={`${Math.round(sis.disco_livre_mb)} MB livres`}
            explica={`Os ficheiros das sessões (templates e PDFs gerados). Apagam-se ao fim de ${estado.limites.validade_min} minutos sem atividade.`}
          />
          <Numero
            rotulo="Sessões ativas"
            valor={String(sis.sessoes_ativas)}
            sub={`máximo ${estado.limites.max_sessoes}`}
            alerta={sis.sessoes_ativas >= Number(estado.limites.max_sessoes)}
            explica="Pessoas (ou separadores) com uma sessão aberta. Cada uma tem uma pasta em disco; no máximo, os novos recebem «ocupado»."
          />
          <Numero
            rotulo="Geração"
            valor={sis.geracao_em_curso ? "a gerar" : "livre"}
            explica="Só se gera uma rifa de cada vez em todo o servidor: enquanto uma corre, as outras pessoas recebem «ocupado»."
          />
          <Numero
            rotulo="Anti-sono"
            valor={estado.acordado.ativo ? `ativo (${estado.acordado.cada_min} min)` : "desligado"}
            sub={
              !estado.acordado.ativo
                ? "só atua no Render"
                : estado.acordado.ultima_em === null
                  ? "ainda sem chamadas"
                  : `${estado.acordado.ultima_ok ? "último pedido ok" : "último pedido FALHOU"} há ${duracao(estado.agora - estado.acordado.ultima_em)}`
            }
            alerta={estado.acordado.ativo && estado.acordado.ultima_ok === false}
            explica="O plano gratuito do Render adormece o serviço após 15 min sem visitas. Para isso não acontecer, o serviço chama o seu próprio /health de 10 em 10 min pelo endereço público. Não acorda um serviço que já adormeceu (ver docs/ONLINE.md)."
          />
          <Numero
            rotulo="Motor"
            valor={sis.motor_vivo ? "a correr" : "parado"}
            sub={`${sis.motor_reinicios} reinício(s)`}
            explica="O processo do motor é recriado quando se cancela tarde, passa do tempo máximo ou falta memória. Muitos reinícios são sinal de problema."
          />
        </div>
        <Medidor
          titulo="Memória face ao limite"
          limite={sis.mem_limite_mb}
          partes={[
            { nome: "Servidor", valor: sis.mem_servidor_mb, cor: CORES[0] ?? "" },
            { nome: "Motor", valor: sis.mem_motor_mb, cor: CORES[1] ?? "" },
          ]}
        />
      </Seccao>

      <Seccao
        id="sistema"
        titulo="Sistema ao longo do tempo"
        explica={`${ROTULO_INTERVALO[intervalo] ?? intervalo}. Passa o rato (ou o dedo) por cima de um gráfico para ver os valores desse instante.`}
      >
        <div className="graficos">
          <Grafico
            titulo="CPU"
            como="Cada ponto é a média da CPU nesse instante, em % de um núcleo. Picos curtos são normais ao gerar; um patamar longo perto de 100 % é um problema."
          >
            <GraficoLinhas
              titulo="CPU"
              series={[{ nome: "CPU", cor: CORES[0] ?? "", pontos: serie(dados?.sistema, "cpu") }]}
              desde={desde}
              ate={ate}
              passo={passo}
              unidade=" %"
            />
          </Grafico>
          <Grafico
            titulo="Memória"
            como="A linha tracejada é o limite do serviço. Se a memória total lhe chega, o Render mata o serviço. O motor sobe a gerar e desce quando é recriado."
          >
            <GraficoLinhas
              titulo="Memória"
              series={[
                { nome: "Servidor", cor: CORES[0] ?? "", pontos: serie(dados?.sistema, "mem_servidor") },
                { nome: "Motor", cor: CORES[1] ?? "", pontos: serie(dados?.sistema, "mem_motor") },
                { nome: "Total", cor: CORES[2] ?? "", pontos: serie(dados?.sistema, "mem_contentor") },
              ]}
              desde={desde}
              ate={ate}
              passo={passo}
              unidade=" MB"
              limite={sis.mem_limite_mb ? { valor: sis.mem_limite_mb, nome: "limite" } : undefined}
            />
          </Grafico>
          <Grafico
            titulo="Sessões ativas"
            como="O máximo de sessões abertas em cada ponto. Mostra as horas de maior procura e se te aproximas do máximo permitido."
          >
            <GraficoLinhas
              titulo="Sessões ativas"
              series={[{ nome: "Sessões", cor: CORES[3] ?? "", pontos: serie(dados?.sistema, "sessoes") }]}
              desde={desde}
              ate={ate}
              passo={passo}
            />
          </Grafico>
        </div>
      </Seccao>

      <Seccao
        id="pedidos"
        titulo="Pedidos à API"
        explica="Tudo o que o site pede ao servidor, sem as perguntas de progresso (de meio em meio segundo) para não dominarem. As páginas e os ficheiros estáticos não contam."
      >
        <div className="graficos">
          <Grafico
            titulo="Pedidos"
            como="Cada barra é o total de pedidos nesse intervalo; a parte vermelha são os que falharam (4xx: o pedido era inválido, p.ex. demasiados pedidos; 5xx: erro do servidor)."
          >
            <GraficoBarras
              titulo="Pedidos"
              pontos={(dados?.pedidos ?? []).map((p) => ({ t: p.t, v: p.n, v2: p.e4 + p.e5 }))}
              desde={desde}
              ate={ate}
              passo={passo}
              nome="pedidos"
              nome2="com erro"
            />
          </Grafico>
          <Grafico
            titulo="Tempo de resposta"
            como="p50 é o tempo típico (metade dos pedidos é mais rápida); p95 é o tempo dos mais lentos (95 % são mais rápidos). Se o p95 sobe muito, há pessoas a esperar."
          >
            <GraficoLinhas
              titulo="Tempo de resposta"
              series={[
                { nome: "p50", cor: CORES[0] ?? "", pontos: serie(dados?.pedidos, "p50") },
                { nome: "p95", cor: CORES[1] ?? "", pontos: serie(dados?.pedidos, "p95") },
              ]}
              desde={desde}
              ate={ate}
              passo={passo}
              unidade=" ms"
            />
          </Grafico>
        </div>
        <div className="tabela-rolavel">
          <table data-testid="admin-tabela-pedidos">
            <caption className="so-leitores">Pedidos por tipo</caption>
            <thead>
              <tr>
                <th scope="col">Pedido</th>
                <th scope="col">Quantos</th>
                <th scope="col">4xx</th>
                <th scope="col">5xx</th>
                <th scope="col">Típico</th>
                <th scope="col">Lentos (p95)</th>
                <th scope="col">Pior</th>
              </tr>
            </thead>
            <tbody>
              {(dados?.tabela_pedidos ?? []).map((l) => (
                <tr key={l.pedido}>
                  <th scope="row">
                    <code>{l.pedido}</code>
                    {l.sondagem && <small> (progresso)</small>}
                  </th>
                  <td>{formatarNumero(l.n)}</td>
                  <td className={l.e4 ? "cor-aviso" : ""}>{l.e4}</td>
                  <td className={l.e5 ? "cor-erro" : ""}>{l.e5}</td>
                  <td>{l.p50 === null ? "—" : `${l.p50} ms`}</td>
                  <td>{l.p95 === null ? "—" : `${l.p95} ms`}</td>
                  <td>{Math.round(l.max_ms)} ms</td>
                </tr>
              ))}
              {!dados?.tabela_pedidos.length && (
                <tr>
                  <td colSpan={7} className="suave">
                    Ainda sem pedidos neste intervalo.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <p className="explica">
          Os tempos são aproximados (agrupados em escalões: 5, 10, 25, 50, 100, 250 ms… 10 s). «Típico» é o
          p50 e «Pior» o mais lento medido.
        </p>
      </Seccao>

      <AdminErros intervalo={intervalo} />

      <Seccao
        id="uso"
        titulo="Utilização"
        explica="O que as pessoas fizeram. Não se guarda nada de pessoal: nem IPs, nem nomes de ficheiros, nem o conteúdo; só contagens, a língua, o tema e o tipo de dispositivo."
      >
        <div className="stats">
          <Numero
            rotulo="Sessões"
            valor={formatarNumero(r?.sessoes ?? 0)}
            explica="Visitas que abriram o gerador (uma sessão por separador aberto, sem contas)."
          />
          <Numero
            rotulo="Pré-visualizações"
            valor={formatarNumero(r?.previas.ok ?? 0)}
            sub={r?.previas.erro ? `${r.previas.erro} com erro` : undefined}
            explica="Quantas vezes se carregou em «Pré-visualizar» com sucesso."
          />
          <Numero
            rotulo="Gerações"
            valor={formatarNumero(geracoesTotal)}
            sub={
              r
                ? `${r.geracoes.ok ?? 0} ok · ${r.geracoes.erros ?? 0} com erros · ${r.geracoes.cancelado ?? 0} canceladas · ${r.geracoes.falhou ?? 0} falhadas`
                : undefined
            }
            explica="Pedidos de «Gerar». «Com erros» acabaram, mas algum PDF não passou a verificação; «falhadas» o motor não as conseguiu acabar; as canceladas foram interrompidas por quem as pediu."
          />
          <Numero
            rotulo="Números gerados"
            valor={formatarNumero(r?.numeros ?? 0)}
            sub={`${formatarNumero(r?.paginas ?? 0)} páginas`}
            explica="A soma dos números e das páginas das gerações que acabaram bem: o trabalho que o motor fez."
          />
          <Numero
            rotulo="Duração de uma geração"
            valor={duracao(r?.duracao.mediana_s ?? null)}
            sub={`as mais lentas: ${duracao(r?.duracao.p95_s ?? null)}`}
            explica="Tempo típico (mediana) e das mais lentas (95 %), só das que acabaram bem. Depende do tamanho do pedido e da CPU disponível."
          />
          <Numero
            rotulo="Descargas"
            valor={formatarNumero((r?.descargas ?? []).reduce((a, d) => a + d.n, 0))}
            sub={(r?.descargas ?? []).map((d) => `${d.chave}: ${d.n}`).join(" · ") || undefined}
            explica="Quantas vezes se descarregou o resultado, em PDF único ou em ZIP."
          />
        </div>
        <div className="graficos">
          <Grafico
            titulo="Funil de utilização"
            como="Quantos eventos há em cada etapa, da abertura do gerador à descarga, e que parte da etapa anterior chegou à seguinte. Conta eventos, não pessoas (não se guarda nada que as identifique): onde cai mais é onde há que melhorar (por exemplo, muitas sessões sem template mostram que o passo do Canva é a barreira)."
          >
            <Funil titulo="Funil de utilização" etapas={r?.funil ?? []} cor={CORES[1]} />
          </Grafico>
          <Grafico
            titulo="Sessões novas"
            como="Cada barra são as sessões abertas nesse intervalo: mostra quando as pessoas chegam."
          >
            <GraficoBarras
              titulo="Sessões novas"
              pontos={(dados?.eventos ?? []).map((p) => ({ t: p.t, v: p.sessoes }))}
              desde={desde}
              ate={ate}
              passo={passo}
              nome="sessões"
            />
          </Grafico>
          <Grafico
            titulo="Gerações e números gerados"
            como="Cada barra são as gerações pedidas nesse intervalo; os números gerados vêm no total ao lado."
          >
            <GraficoBarras
              titulo="Gerações"
              pontos={(dados?.eventos ?? []).map((p) => ({ t: p.t, v: p.geracoes }))}
              desde={desde}
              ate={ate}
              passo={passo}
              nome="gerações"
              cor={CORES[1]}
            />
          </Grafico>
          <Grafico
            titulo="Quanto demoram as gerações"
            como="Quantas gerações acabaram em cada escalão de tempo. Barras para a direita significam pedidos pesados ou CPU curta."
          >
            <BarrasH titulo="Duração das gerações" itens={r?.duracao.histograma ?? []} cor={CORES[2]} />
          </Grafico>
        </div>
        <div className="graficos">
          <Grafico
            titulo="Línguas"
            como="A língua da interface em cada sessão (o 1.º pedido). Diz onde vale a pena rever as traduções."
          >
            <BarrasH titulo="Línguas" itens={r?.linguas ?? []} />
          </Grafico>
          <Grafico
            titulo="Países"
            como={`De que país vêm as sessões, pelo cabeçalho CF-IPCountry que a rede do alojamento acrescenta (guarda-se só o código do país, nunca o IP). «Desconhecido» são sessões sem esse cabeçalho (rede privada, Tor) ou, se tudo está nesse grupo, o alojamento não o envia: ${
              estado.proxy.pais_pct === null
                ? "sem pedidos para medir"
                : `${estado.proxy.pais_pct} % dos pedidos da última hora o traziam`
            }.`}
          >
            <BarrasH titulo="Países" itens={nomesDosPaises(r?.paises ?? [])} cor={CORES[2] ?? ""} />
          </Grafico>
          <Grafico
            titulo="Temas"
            como="O tema visual escolhido ao abrir a sessão. «outro» são valores que o servidor não reconhece."
          >
            <BarrasH titulo="Temas" itens={r?.temas ?? []} cor={CORES[1]} />
          </Grafico>
          <Grafico
            titulo="Dispositivos"
            como="Computador ou telemóvel (pelo navegador). Os robôs dos motores de pesquisa não entram."
          >
            <Rosca titulo="Dispositivos" itens={(r?.dispositivos ?? []).filter((d) => d.chave !== "robo")} />
          </Grafico>
          <Grafico
            titulo="Páginas vistas"
            como={`Visitas às páginas do site (sem robôs: ${r?.robos ?? 0} no intervalo). Mostra se o tutorial e o vídeo são usados.`}
          >
            <BarrasH titulo="Páginas vistas" itens={r?.paginas_vistas ?? []} cor={CORES[3]} />
          </Grafico>
          <Grafico
            titulo="Erros devolvidos"
            como="Respostas de erro por código: 404 (sessão expirada), 413 (ficheiro grande demais), 422 (pedido inválido), 429 (demasiados pedidos), 503 (ocupado), 500 (erro nosso)."
          >
            <BarrasH titulo="Erros devolvidos" itens={r?.erros_http ?? []} cor="var(--erro)" />
          </Grafico>
          <Grafico
            titulo="Porque falham as gerações"
            como="Motivo das gerações que o motor não acabou (uma regra do pedido, tempo excedido, o motor morreu…)."
          >
            <BarrasH titulo="Falhas" itens={r?.falhas ?? []} cor="var(--erro)" />
          </Grafico>
        </div>
      </Seccao>

      <Seccao
        id="ecras"
        titulo="Ecrãs e dispositivos"
        explica="Com que ecrãs e aparelhos o site é visitado (uma contagem por separador aberto, sem robôs). Guardam-se só o tamanho do ecrã e da janela, a família do aparelho e, nos Chrome que o dizem, o modelo do telemóvel: nunca o IP nem o navegador completo."
      >
        <div className="graficos">
          <Grafico
            titulo="Tipo de ecrã"
            como="Telemóvel, tablet ou computador (este por tamanho: Full HD, QHD, 4K, ultra-wide). Mostra se vale a pena afinar o desenho para telemóveis ou para ecrãs grandes."
          >
            <Rosca titulo="Tipo de ecrã" itens={r?.classes_de_ecra ?? []} />
          </Grafico>
          <Grafico
            titulo="Ecrãs mais comuns"
            como="Tamanho do ecrã em pixéis CSS e a densidade de pixéis (3x é típico dos iPhone recentes, 2x–3x dos Android topo de gama). Os telemóveis recentes repetem-se muito: 393×852 @3x é o iPhone 15/16."
          >
            <BarrasH titulo="Ecrãs mais comuns" itens={r?.ecras ?? []} cor={CORES[1]} />
          </Grafico>
          <Grafico
            titulo="Aparelhos"
            como="A família (iPhone, iPad, Android, Windows, Mac…) ou, nos Chrome de Android que o dizem, o modelo do telemóvel (p.ex. «Pixel 9»). O iPhone nunca diz o modelo."
          >
            <BarrasH titulo="Aparelhos" itens={r?.dispositivos_detalhe ?? []} cor={CORES[2]} />
          </Grafico>
          <Grafico
            titulo="Largura da janela"
            como="A largura da janela do browser (não a do ecrã). Janelas estreitas num ecrã grande são pessoas com o browser a meio do ecrã."
          >
            <BarrasH titulo="Largura da janela" itens={r?.janelas ?? []} cor={CORES[3]} />
          </Grafico>
          <Grafico
            titulo="Toque"
            como="Ecrãs com toque (telemóveis, tablets e alguns portáteis) ou só com rato e teclado."
          >
            <Rosca titulo="Toque" itens={r?.toque ?? []} />
          </Grafico>
        </div>
      </Seccao>

      <Seccao
        id="proxy"
        titulo="Proxy e limite por IP"
        explica="O servidor limita os pedidos por IP. Atrás do Render, o IP real vem no cabeçalho X-Forwarded-For; se o servidor não confiar no proxy, todos os visitantes parecem o mesmo e o limite passa a ser de todos."
      >
        <p className={`veredicto cor-${proxy.cor}`} role="status" data-testid="admin-proxy">
          {proxy.texto}
        </p>
        <dl className="medidas">
          <div>
            <dt>Pedidos analisados (última hora)</dt>
            <dd>{estado.proxy.pedidos}</dd>
          </div>
          <div>
            <dt>Endereços distintos (por hash)</dt>
            <dd>{estado.proxy.ips_distintos}</dd>
          </div>
          <div>
            <dt>Com X-Forwarded-For</dt>
            <dd>{estado.proxy.xff_pct === null ? "—" : `${estado.proxy.xff_pct} %`}</dd>
          </div>
          <div>
            <dt>Com o país (CF-IPCountry)</dt>
            <dd>{estado.proxy.pais_pct === null ? "—" : `${estado.proxy.pais_pct} %`}</dd>
          </div>
          <div>
            <dt>Com IP interno (10.x, 172.16.x, 192.168.x)</dt>
            <dd>{estado.proxy.privados_pct === null ? "—" : `${estado.proxy.privados_pct} %`}</dd>
          </div>
        </dl>
      </Seccao>

      <Seccao
        id="limites"
        titulo="Limites em vigor"
        explica="Os valores que o servidor está a aplicar agora (variáveis de ambiente do serviço)."
      >
        <dl className="medidas">
          {LIMITES.map(([chave, rotulo, unidade]) => (
            <div key={chave}>
              <dt>{rotulo}</dt>
              <dd>
                {String(estado.limites[chave])}
                {unidade}
              </dd>
            </div>
          ))}
          <div>
            <dt>Python / sistema</dt>
            <dd>
              {sis.python} · {sis.plataforma}
            </dd>
          </div>
        </dl>
      </Seccao>

      <Seccao
        id="api-publica"
        titulo="API pública (Swagger UI)"
        explica="A documentação interativa da API pública v1 (geração em lote com chave X-API-Key; ver docs/API.md): lista os pedidos, os campos e as respostas, e deixa experimentá-los. Está aberta a quem tiver o endereço. As chaves criam-se e revogam-se no painel (secção das chaves da API)."
      >
        <div className="botoes">
          <a href="/api/v1/docs" target="_blank" rel="noopener noreferrer" data-testid="admin-swagger">
            Abrir o Swagger UI
          </a>
          <a
            href="/api/v1/openapi.json"
            target="_blank"
            rel="noopener noreferrer"
            data-testid="admin-openapi"
          >
            Descrição OpenAPI (JSON)
          </a>
        </div>
      </Seccao>

      <AdminSeo leitura={estado.papel === "leitura"} />
    </div>
  );
}
