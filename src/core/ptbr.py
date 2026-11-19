"""Português do Brasil (`pt-br`) derivado do português de Portugal (`pt`) por um glossário.

O texto de `pt-br` NÃO se escreve à mão: parte-se do `pt` (a fonte) e aplicam-se as regras abaixo (`derivar`), para que a interface fique coerente por construção (se «Descarregar»
vira «Baixar» num botão, vira também no tutorial) e cada texto novo em `pt` ganhe a versão brasileira sem trabalho. O que o glossário não apanha corrige-se em `OVERRIDES` (por
chave, em `core/idiomas/pt_br.py`) ou nas tabelas de cada módulo; `tests/test_ptbr.py` tem uma lista negra de palavras de Portugal que não podem sobrar em nenhum texto derivado.

Regras: (1) frases fixas; (2) palavras que mudam de género levam o artigo atrás («a ligação» → «o link»); (3) famílias de verbos («descarregar» → «baixar», «carregar em» → «clicar em»,
«carregar» → «enviar», «registar» → «registrar»); (4) gerúndio («a gerar» → «gerando»); (5) palavras soltas e ortografia. Nunca se mexe em `{parâmetros}`, `<etiquetas>`,
endereços, nem em código entre crases.
"""
from __future__ import annotations

import re

# ------------------------------------------------------------------ o que se protege
_PROTEGIDO = re.compile(r"(\{[^{}]*\}|<[^<>]*>|https?://\S+|`[^`]*`|\[[^\]]*\]\([^)]*\))")


def _caso(original: str, novo: str) -> str:
    """Mantém as maiúsculas de `original` (tudo maiúsculas, 1.ª maiúscula ou minúsculas)."""
    if len(original) > 1 and original.isupper():
        return novo.upper()
    if original[:1].isupper():
        return novo[:1].upper() + novo[1:]
    return novo


# ------------------------------------------------------------------ (1) frases fixas
FRASES = [
    (r"ligação à internet", "conexão com a internet"),
    (r"verifique a ligação", "verifique a conexão"),
    (r"ligação copiada", "link copiado"),
    (r"câmaras? municip(?:al|ais)", "prefeitura"),
    (r"juntas? de freguesia", "associação de bairro"),
    (r"acerca de", "sobre"),
    (r"visitas? de estudo", "passeio escolar"),
    (r"de aldeia ou num arraial", "de comunidade ou numa festa junina"),
    (r"comissões? de festas", "comissão organizadora"),
    (r"próxima época", "próxima temporada"),
    (r"arranca depressa", "inicia rápido"),
    (r"para a partilhar", "para compartilhá-la"),
    (r"para o partilhar", "para compartilhá-lo"),
    (r"partilha d", "compartilhamento d"),
    (r"quem gere\b", "quem administra"),
    (r"é gerido", "é administrado"),
    (r"contactar-nos", "nos contatar"),
    (r"fale connosco", "fale conosco"),
    (r"ranchos folclóricos", "grupos folclóricos"),
    (r"lotaria nacional", "loteria federal"),
    (r"\(rgpd, artigo 6\.º, n\.º 1, alínea a\)", "(LGPD, art. 7º, inciso I)"),
    (r"\(rgpd, artigo 6\.º, n\.º 1, alínea f\)", "(LGPD, art. 7º, inciso IX)"),
    (r"comissão nacional de proteção de dados \(cnpd\.pt\)", "Autoridade Nacional de Proteção de Dados (gov.br/anpd)"),
    (r"regulamento geral (?:sobre a|de) proteção de dados \(rgpd\)", "Lei Geral de Proteção de Dados (LGPD)"),
    (r"regulamento geral (?:sobre a|de) proteção de dados", "Lei Geral de Proteção de Dados"),
    (r"comissão nacional de proteção de dados \(cnpd\)", "Autoridade Nacional de Proteção de Dados (ANPD)"),
    (r"comissão nacional de proteção de dados", "Autoridade Nacional de Proteção de Dados"),
]

# ------------------------------------------------------------------ (2) mudança de género: o artigo vem atrás
_FEM_PARA_MASC = {"a": "o", "as": "os", "uma": "um", "umas": "uns", "esta": "este", "estas": "estes", "essa": "esse", "essas": "esses", "aquela": "aquele",
                  "na": "no", "nas": "nos", "da": "do", "das": "dos", "pela": "pelo", "pelas": "pelos", "à": "ao", "às": "aos", "numa": "num", "numas": "nuns",
                  "desta": "deste", "destas": "destes", "dessa": "desse", "nesta": "neste", "nessa": "nesse", "toda": "todo", "todas": "todos", "outra": "outro", "outras": "outros",
                  "sua": "seu", "suas": "seus", "nossa": "nosso", "mesma": "mesmo"}
_MASC_PARA_FEM = {"o": "a", "os": "as", "um": "uma", "uns": "umas", "este": "esta", "estes": "estas", "esse": "essa", "esses": "essas", "aquele": "aquela",
                  "no": "na", "nos": "nas", "do": "da", "dos": "das", "pelo": "pela", "pelos": "pelas", "ao": "à", "aos": "às", "num": "numa", "nuns": "numas",
                  "deste": "desta", "destes": "destas", "desse": "dessa", "neste": "nesta", "nesse": "nessa", "todo": "toda", "todos": "todas", "outro": "outra", "outros": "outras",
                  "seu": "sua", "seus": "suas", "nosso": "nossa", "mesmo": "mesma"}
# (palavra de Portugal, singular, plural, género do que sai: "m" ou "f"): o artigo antes dela passa para o género certo
_GENERO = [
    ("ligação", "link", "links", "m"), ("ligações", "link", "links", "m"),
    ("ecrã", "tela", "telas", "f"), ("ecrãs", "tela", "telas", "f"),
    ("separador", "aba", "abas", "f"), ("separadores", "aba", "abas", "f"),
    ("preçário", "lista de preços", "listas de preços", "f"), ("preçários", "lista de preços", "listas de preços", "f"),
]


def _genero(texto: str) -> str:
    for pt, singular, plural, genero in _GENERO:
        novo = plural if pt.endswith("s") else singular
        mapa = _FEM_PARA_MASC if genero == "m" else _MASC_PARA_FEM
        origem = "f" if genero == "m" else "m"
        dets = "|".join(sorted((re.escape(d) for d in (_MASC_PARA_FEM if origem == "m" else _FEM_PARA_MASC)), key=len, reverse=True))
        texto = re.sub(rf"\b({dets})(\s+)({pt})\b", lambda m: _caso(m.group(1), mapa[m.group(1).lower()]) + m.group(2) + _caso(m.group(3), novo), texto, flags=re.I)
        texto = re.sub(rf"\b{pt}\b", lambda m: _caso(m.group(0), novo), texto, flags=re.I)
    return texto


# ------------------------------------------------------------------ (3) famílias de verbos
_SUFIXOS_BAIXAR = {"ar": "ar", "a": "a", "ue": "e", "am": "am", "ou": "ou", "ado": "ado", "ados": "ados", "ada": "ada", "adas": "adas", "ando": "ando", "amos": "amos"}
_CLICAR = {"ar": "clicar", "a": "clica", "ue": "clique", "am": "clicam", "ou": "clicou", "ando": "clicando"}
_ENVIAR = {"ar": "enviar", "a": "envia", "ue": "envie", "am": "enviam", "ou": "enviou", "ado": "enviado", "ados": "enviados", "ada": "enviada", "adas": "enviadas", "ando": "enviando", "amos": "enviamos"}
_REGISTRAR = {"ar": "ar", "o": "o", "os": "os", "ado": "ado", "ados": "ados", "ada": "ada", "adas": "adas", "amos": "amos", "e": "e", "am": "am", "ou": "ou"}
_GUARDAR = {"ar": "salvar", "a": "salva", "e": "salve", "am": "salvam", "amos": "armazenamos", "ado": "salvo", "ados": "salvos", "ada": "salva", "adas": "salvas", "ou": "salvou"}
_ACEDER = {"eder": "acessar", "ede": "acessa", "eda": "acesse", "edem": "acessam", "edeu": "acessou"}


def _verbos(texto: str) -> str:
    # «carregar em» (carregar num botão) é «clicar em»; o resto de «carregar» (enviar um ficheiro) é «enviar»
    texto = re.sub(r"\bcarreg(ar|a|ue|am|ou|ando)(\s+(?:em|no|na|nos|nas)\b)", lambda m: _caso(m.group(0), _CLICAR[m.group(1)] + (" em" if m.group(2).strip() == "em" else m.group(2))), texto, flags=re.I)
    texto = re.sub(r"\bcarreg(ar|a|ue|am|ou|ado|ados|ada|adas|ando|amos)\b", lambda m: _caso(m.group(0), _ENVIAR[m.group(1).lower()]), texto, flags=re.I)
    texto = re.sub(r"\bdescarreg(ar|a|ue|am|ou|ado|ados|ada|adas|ando|amos)\b", lambda m: _caso(m.group(0), "baix" + _SUFIXOS_BAIXAR[m.group(1).lower()].replace("ue", "e")), texto, flags=re.I)
    texto = re.sub(r"\bdescargas?\b", lambda m: _caso(m.group(0), "downloads" if m.group(0).lower().endswith("s") else "download"), texto, flags=re.I)
    texto = re.sub(r"\bregist(ar|o|os|ado|ados|ada|adas|amos|e|am|ou)\b", lambda m: _caso(m.group(0), "registr" + _REGISTRAR[m.group(1).lower()]), texto, flags=re.I)
    texto = re.sub(r"\bguard(ar|a|e|am|amos|ado|ados|ada|adas|ou)\b", lambda m: _caso(m.group(0), _GUARDAR[m.group(1).lower()]), texto, flags=re.I)
    texto = re.sub(r"\bac(eder|ede|eda|edem|edeu)\b", lambda m: _caso(m.group(0), _ACEDER[m.group(1).lower()]), texto, flags=re.I)
    return texto


# ------------------------------------------------------------------ (4) gerúndio
_GERUNDIO = {"ar": "ando", "er": "endo", "ir": "indo"}
_VERBOS_DE_ESTADO = r"está|estão|estou|estamos|estava|estavam|continua|continuam|fica|ficam"
_VERBOS_DE_PROGRESSO = r"gerar|analisar|ler|cancelar|verificar|preparar|calcular|comprimir|gravar|criar|enviar|desenhar|recortar|processar|converter|abrir|ligar|esperar|aguardar|carregar|descarregar|guardar"


def _gerundio(texto: str) -> str:
    def trocar(verbo: str) -> str:
        return verbo[:-2] + _GERUNDIO[verbo[-2:].lower()]

    texto = re.sub(rf"\b({_VERBOS_DE_ESTADO})(\s+)a(\s+)([a-zà-ú]+(?:ar|er|ir))\b", lambda m: m.group(1) + m.group(2) + trocar(m.group(4)), texto, flags=re.I)
    inicio = r"(^|[.!?…:;]\s+|\n\s*|[«\"(]\s*)"
    return re.sub(inicio + rf"A\s+({_VERBOS_DE_PROGRESSO})\b", lambda m: m.group(1) + trocar(m.group(2)).capitalize(), texto)


# ------------------------------------------------------------------ (5) palavras soltas e ortografia
PALAVRAS = {
    "ficheiro": "arquivo", "ficheiros": "arquivos", "utilizador": "usuário", "utilizadores": "usuários",
    "rato": "mouse", "telemóvel": "celular", "telemóveis": "celulares", "palavra-passe": "senha", "palavras-passe": "senhas",
    "equipa": "equipe", "equipas": "equipes", "talão": "canhoto", "talões": "canhotos", "lotaria": "loteria", "lotarias": "loterias",
    "escuteiros": "escoteiros", "escuteiro": "escoteiro", "apelido": "sobrenome", "grelha": "grade", "grelhas": "grades",
    "sítio": "lugar", "sítios": "lugares", "freguesia": "bairro", "freguesias": "bairros",
    "controlo": "controle", "contacto": "contato", "contactos": "contatos", "connosco": "conosco", "quota": "cota", "quotas": "cotas",
    "aspeto": "aspecto", "aspetos": "aspectos", "deteta": "detecta", "detetar": "detectar", "detetado": "detectado", "facto": "fato", "factos": "fatos",
    "prémio": "prêmio", "prémios": "prêmios", "económico": "econômico", "económica": "econômica", "secção": "seção", "secções": "seções",
    "polaco": "polonês", "checo": "tcheco", "perspetiva": "perspectiva", "gerir": "administrar", "gerido": "administrado", "largar": "soltar",
    "acerca": "sobre", "angariar": "arrecadar", "angariação": "arrecadação", "angariado": "arrecadado", "angaria": "arrecada", "cabaz": "cesta", "cabazes": "cestas", "aldeia": "comunidade", "rgpd": "LGPD", "cnpd": "ANPD", "depressa": "rápido", "browser": "navegador", "browsers": "navegadores", "logótipo": "logotipo", "logótipos": "logotipos", "partilhar": "compartilhar", "partilhe": "compartilhe", "partilhado": "compartilhado", "partilhados": "compartilhados", "partilha": "compartilha", "partilham": "compartilham", "partilhamos": "compartilhamos", "partilhas": "compartilhamentos", "agradeça": "agradeça", "em baixo": "embaixo", "autocarro": "ônibus", "bué": "muito",
    "rapariga": "garota", "miúdos": "crianças", "casa de banho": "banheiro", "cartão de crédito": "cartão de crédito",
    "pré-visualizar": "pré-visualizar", "ecrã": "tela", "ecrãs": "telas",
}
_PALAVRAS_RE = re.compile(r"\b(" + "|".join(sorted((re.escape(p) for p in PALAVRAS), key=len, reverse=True)) + r")\b", re.I)


def _soltas(texto: str) -> str:
    return _PALAVRAS_RE.sub(lambda m: _caso(m.group(0), PALAVRAS[m.group(0).lower()]), texto)


def _frases(texto: str) -> str:
    for padrao, novo in FRASES:
        texto = re.sub(rf"(?<!\w){padrao}", lambda m, n=novo: _caso(m.group(0), n), texto, flags=re.I)
    # «pedir-nos», «diga-nos»: no Brasil o pronome vai antes do verbo («nos pedir», «nos diga»)
    return re.sub(r"\b([A-Za-zÀ-ÿ]+)-(nos)\b", lambda m: (m.group(2).capitalize() if m.group(1)[:1].isupper() else m.group(2)) + " " + m.group(1)[:1].lower() + m.group(1)[1:], texto)


def derivar(texto: str) -> str:
    """O texto de Portugal passado para o português do Brasil (só o que está fora de `{parâmetros}`, `<etiquetas>`, endereços e crases)."""
    if not isinstance(texto, str) or not texto:
        return texto
    partes = _PROTEGIDO.split(texto)
    for i in range(0, len(partes), 2):                      # as posições pares são texto livre; as ímpares, o que se protege
        p = partes[i]
        p = _frases(p)
        p = _genero(p)
        p = _verbos(p)
        p = _gerundio(p)
        p = _soltas(p)
        partes[i] = p
    return "".join(partes)


def derivar_tudo(o):
    """`derivar` em todos os textos de um dicionário, lista, tuplo ou texto (a estrutura mantém-se; chaves e números ficam)."""
    if isinstance(o, str):
        return derivar(o)
    if isinstance(o, dict):
        return {k: derivar_tudo(v) for k, v in o.items()}
    if isinstance(o, list):
        return [derivar_tudo(v) for v in o]
    if isinstance(o, tuple):
        return tuple(derivar_tudo(v) for v in o)
    return o


# palavras de Portugal que NÃO podem sobrar num texto brasileiro (a lista negra do teste); (nunca «bilhete», «rifa», «sorteio»: também se usam no Brasil)
LISTA_NEGRA = (
    "ficheiro", "ecrã", "utilizador", "descarreg", "telemóvel", "palavra-passe", "separador", "grelha", "facto", "equipa", "rato", "talão", "talões", "lotaria",
    "câmara municipal", "ligação", "ligações", "contacto", "controlo", "registo", "registar", "guardar", "apelido", "aceder", "carregue em", "carregar em", "quotas",
    "aspeto", "deteta", "prémio", "secção", "polaco", "checo", "freguesia", "escuteiros", "connosco", "sítio", "rgpd", "cnpd",
)
