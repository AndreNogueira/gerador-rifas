"""Termos, privacidade e contacto em português (a língua original; as outras são traduções destes textos, ver `legal/__init__.py`).

Escrito **sem apoio jurídico** e por isso provisório: tem de ser revisto por um advogado e por um contabilista antes de o serviço cobrar
(docs/PLANO_PRODUTO.md §5). Nenhum dado pessoal está aqui: o nome do responsável e o e-mail vêm das variáveis de ambiente `RESPONSAVEL`
e `CONTACTO_EMAIL`. Os `{marcadores}` são preenchidos por `textos_legais.pagina`: {responsavel}, {contacto}, {contacto_pagina}, {max_numeros},
{validade}, {atualizado}. Cada tradução tem de ter as mesmas páginas, secções, parágrafos e marcadores (um teste verifica-o).
"""
FRASES = {
    "responsavel_com": "O serviço é gerido por {nome}.",
    "responsavel_sem": "O serviço é gerido pelo seu autor, a pessoa que o disponibiliza em linha.",
    "contacto_com": "Pode contactar-nos em {email}.",
    "contacto_sem": "De momento não há um contacto público.",
    "contacto_pagina_com": "Para dúvidas, erros ou sugestões, escreva para {email}.",
    "contacto_pagina_sem": "De momento não há um contacto público. Volte a esta página mais tarde.",
    "atualizado": "8 de novembro de 2026",
}

AVISO = "Versão provisória, por rever com apoio jurídico. Se algo aqui for diferente do que o serviço faz, o que vale é pedir-nos que o corrijamos."

TEXTOS = {
    "termos": {
        "titulo": "Termos de utilização",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "O que é este serviço",
             "paragrafos": ["O Gerador de Rifas cria, a partir de um template em PDF, os bilhetes de uma rifa numerados e prontos a imprimir. "
                            "Faz só isso: não vende bilhetes, não recebe dinheiro, não guarda listas de participantes e não faz sorteios com valor legal.",
                            "{responsavel}"]},
            {"titulo": "Quem organiza a rifa é responsável por ela",
             "paragrafos": ["As rifas, as tômbolas e os sorteios estão sujeitos a regras legais (por exemplo, licenças da câmara municipal e regras para "
                            "associações) que variam consoante o caso. Quem organiza a rifa é o único responsável por cumprir a lei, por cobrar e por "
                            "entregar os prémios. Este serviço não dá aconselhamento jurídico."]},
            {"titulo": "Uso permitido",
             "paragrafos": ["O serviço é gratuito e para uso razoável. Não pode ser usado para gerar bilhetes de fraudes, nem para sobrecarregar o servidor: "
                            "há limites de tamanho dos ficheiros, de números por pedido ({max_numeros}) e de pedidos por minuto, "
                            "e uma geração de cada vez."]},
            {"titulo": "Os seus ficheiros",
             "paragrafos": ["O template e os algarismos servem só para gerar as suas rifas e são apagados do servidor passados {validade} "
                            "minutos sem atividade, ou quando carrega em «Limpar tudo». Não os usamos para mais nada. Continuam a ser seus: só tem de "
                            "ter o direito de usar o que carrega (imagens, letras, logótipos)."]},
            {"titulo": "Sem garantias",
             "paragrafos": ["O serviço é fornecido «como está», sem garantia de que esteja sempre disponível ou livre de erros. Confira sempre os PDFs "
                            "antes de imprimir (o serviço verifica os números gerados, mas a conferência final é sua). Na medida permitida pela lei, não "
                            "respondemos por perdas ligadas ao uso do serviço."]},
            {"titulo": "Alterações",
             "paragrafos": ["Estes termos podem mudar; a data da última atualização é {atualizado}. Se um dia o serviço passar a ser pago, "
                            "isso será dito de forma clara antes de cobrar."]},
            {"titulo": "Contacto", "paragrafos": ["{contacto}"]},
        ],
    },
    "privacidade": {
        "titulo": "Política de privacidade",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Resumo",
             "paragrafos": ["Não há contas, nem anúncios, nem ferramentas de seguimento de terceiros. Os seus ficheiros são apagados do servidor em "
                            "{validade} minutos. As estatísticas de utilização são só números agregados."]},
            {"titulo": "Que dados tratamos",
             "paragrafos": ["Os ficheiros que carrega (template e algarismos) são tratados só para gerar as rifas, ficam numa pasta temporária do servidor e "
                            "são apagados passados {validade} minutos sem atividade ou quando carrega em «Limpar tudo».",
                            "Para saber como o serviço é usado, registamos contagens: quantas visitas, gerações e descargas, a língua e o tema escolhidos e o "
                            "tipo de ecrã. Registamos também o país da visita (só o código, por exemplo «PT»), que a rede do alojamento deduz do endereço IP; o IP em si não o guardamos. Nunca registamos endereços IP, nomes de ficheiros, o conteúdo dos ficheiros nem o programa de navegação completo.",
                            "O endereço IP é usado apenas em memória, durante instantes, para limitar o número de pedidos por minuto, e não é guardado por nós. "
                            "O fornecedor de alojamento (Render, em Frankfurt, na União Europeia) pode registar endereços IP nos seus registos técnicos."]},
            {"titulo": "No seu browser",
             "paragrafos": ["Guardamos no seu browser (armazenamento local) as suas preferências: a língua, o tema visual, o modo claro ou escuro e os "
                            "últimos valores do formulário. Para não repetir o trabalho de um ano para o outro, o ficheiro dos algarismos também pode ficar "
                            "guardado no seu browser (nunca no nosso servidor); «Limpar tudo» apaga-o. Não usamos cookies de publicidade nem de seguimento."]},
            {"titulo": "Base legal e conservação",
             "paragrafos": ["Tratamos estes dados por interesse legítimo em prestar o serviço e o manter seguro (RGPD, artigo 6.º, n.º 1, alínea f). "
                            "Os ficheiros duram minutos; as contagens agregadas não identificam ninguém."]},
            {"titulo": "Os seus direitos",
             "paragrafos": ["Tem direito de acesso, retificação, apagamento, oposição e de apresentar queixa à Comissão Nacional de Proteção de Dados (cnpd.pt). "
                            "Como não guardamos dados que o identifiquem, na prática há pouco a aceder ou apagar; se tiver dúvidas, fale connosco."]},
            {"titulo": "Quem responde", "paragrafos": ["{responsavel}", "{contacto}"]},
            {"titulo": "Atualização", "paragrafos": ["Última atualização: {atualizado}."]},
        ],
    },
    "contacto": {
        "titulo": "Contacto",
        "aviso": "",
        "seccoes": [
            {"titulo": "Fale connosco",
             "paragrafos": ["{contacto_pagina}",
                            "Se encontrar um erro, diga-nos o que fez e o que esperava; não envie o seu template com dados pessoais."]},
        ],
    },
}
