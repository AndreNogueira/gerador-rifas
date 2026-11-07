T = {
    "m_ficheiro": "Ficheiro", "m_ver": "Ver", "m_idioma": "Idioma", "m_ajuda": "Ajuda",
    "mi_abrir_template": "Abrir template…", "mi_abrir_alg": "Escolher ficheiro dos algarismos…",
    "mi_destino": "Escolher pasta de destino…", "mi_sair": "Sair",
    "mi_zoom_mais": "Aumentar zoom", "mi_zoom_menos": "Diminuir zoom", "mi_ajustar": "Ajustar à janela",
    "mi_expandir": "Expandir a pré-visualização", "mi_reduzir": "Reduzir a pré-visualização",
    "mi_tema": "Tema", "mi_tema_sistema": "Igual ao Windows", "mi_tema_claro": "Claro", "mi_tema_escuro": "Escuro",
    "mi_tutorial": "Tutorial passo a passo", "mi_sobre": "Acerca de…",
    "sobre_texto": ("{app}\nVersão {versao}\n\nGera PDFs de rifas numerados a partir de um template do Canva.\n\n"
                    "Usa as bibliotecas pypdf, pypdfium2, Pillow e CustomTkinter (licenças permissivas)."),
    "tip_tema": "Alternar entre tema claro e escuro",
    "tut_titulo": "Tutorial", "tut_ant": "Anterior", "tut_seg": "Seguinte",
    "tut_t0": "Visão geral",
    "tut_b0": ("Este programa pega no seu desenho de rifa feito no Canva e gera os PDFs prontos a imprimir, "
               "com os números que quiser.\n\n"
               "São só 4 passos, pela ordem em que aparecem à esquerda:\n\n"
               "• 1 – escolha o template (o PDF do Canva);\n"
               "• 2 – escolha o ficheiro com os algarismos 0 a 9;\n"
               "• 3 – diga de que número a que número, e se quer vários PDFs ou um só;\n"
               "• 4 – escolha a pasta e escreva o nome dos ficheiros.\n\n"
               "Depois carregue em «{previa}» para ver uma página e em «{gerar}». "
               "No fim, cada PDF é verificado automaticamente."),
    "tut_b1": ("No Canva, desenhe a rifa e escreva em cada bilhete os números de exemplo 0001, 0002, 0003, … "
               "(um por bilhete). Cada número aparece 2 vezes: uma no talão e outra na parte principal do bilhete "
               "(como mostra a imagem).\n\n"
               "Descarregue em PDF e escolha esse ficheiro no passo 1.\n\n"
               "• O programa deteta sozinho quantos bilhetes há por página e a orientação do texto do talão.\n"
               "• Os números têm de ser texto, não imagem.\n"
               "• Outros números do desenho (ano, telefone…) ficam como estão.\n"
               "• Só a 1.ª página do PDF é usada."),
    "tut_b3": ("• {de} / {ate}: o primeiro e o último número a gerar (por exemplo 1 a 1000).\n"
               "• {algarismos}: com quantos algarismos escrever (4 → 0001). Por defeito é o do desenho do template; "
               "se pedir mais, o tamanho dos números reduz para caberem.\n"
               "• {varios}: parte em ficheiros com o máximo de números que indicar (múltiplo dos bilhetes por página).\n"
               "• {unico}: tudo num só ficheiro.\n\n"
               "Em baixo vê o resumo: quantos números, ficheiros e páginas vão ser gerados."),
    "tut_b4": ("Escolha a pasta onde guardar os PDFs e escreva o nome dos ficheiros (obrigatório; o programa nunca "
               "sugere um). Os ficheiros ficam «NOME - 0001 - 0300.pdf», «NOME - 0301 - 0600.pdf», … ou só "
               "«NOME - 0001 - 1000.pdf» se escolher um único PDF.\n\n"
               "Se já existirem ficheiros com esses nomes, o programa pergunta antes de os substituir."),
    "tut_t5": "Pré-visualizar e gerar",
    "tut_b5": ("«{previa}» mostra a 1.ª página com números verdadeiros, para confirmar a letra, o tamanho e a posição "
               "antes de gerar tudo.\n\n"
               "No visor:\n"
               "• − / + ou Ctrl + roda do rato: zoom;\n"
               "• arraste para deslocar; duplo clique ou «{ajustar}»: ver a folha inteira;\n"
               "• o botão de expandir dá toda a janela à pré-visualização; clique outra vez para voltar;\n"
               "• a divisória entre as definições e o visor também se arrasta.\n\n"
               "Carregue em «{gerar}». A barra mostra o progresso (pode cancelar). No fim, cada PDF é verificado "
               "automaticamente (páginas e números) e aparece o botão «{pasta}»."),
    "tut_t6": "Dicas e problemas",
    "tut_b6": ("• «Não encontrei os números de exemplo»: no Canva os números têm de ser texto, no formato 0001, 0002, … "
               "(cada um 2 vezes).\n"
               "• Os números saem com outra letra: o ficheiro dos algarismos tem de usar exatamente a mesma letra do "
               "template. Confirme na pré-visualização.\n"
               "• Números pequenos ou estranhos: com PNG/JPG use uma imagem grande (≥ 100 px de altura); o PDF é sempre melhor.\n"
               "• «Não consegui gravar»: feche o PDF se estiver aberto noutro programa.\n"
               "• Mais algarismos do que o desenho: o tamanho reduz automaticamente (aviso no registo).\n"
               "• Pode mudar a língua e o tema (claro/escuro) nos menus; as cores acompanham o Windows."),
    'err_folha_varias': 'Só um template com uma única rifa pode ser repetido na folha.',
    'err_rifa_grande': 'A rifa ({w} × {h} mm) não cabe numa folha {papel} com margens de {margem} mm.\n\nEscolha um papel maior, reduza a margem ou desenhe a rifa mais pequena.',
    'log_folha': 'Folha {papel}: {n} rifas por folha ({w} × {h} mm cada).',
    'aviso_muitas': '⚠ {n} rifas por folha: ficam muito pequenas e difíceis de recortar. Confirme o tamanho da rifa.',
    'c1_ok_uma': '✔ Template com 1 rifa · número de exemplo {primeiro}',
    'lay_info': 'O template tem uma só rifa: o programa enche a folha com cópias, o máximo que couber.',
    'lay_papel': 'Papel',
    'lay_margem': 'Margem (mm)',
    'lay_por_folha': 'Rifas por folha',
    'lay_resultado': 'Rifa de {w} × {h} mm → {n} por folha {papel} (máximo {max})',
    'lay_recortada': ' · recortada ao desenho',
    'lay_rodadas': ' · {r} rodadas 90°',
    'lay_acima': 'Só cabem {max} por folha.',
    'conf_muitas': 'Vai gerar {n} rifas por folha ({w} × {h} mm cada). É um valor muito alto: ficam pequenas e difíceis de recortar.\n\nContinuar?',
    'mi_video': 'Vídeo tutorial',
    'video_falta': 'Não encontrei o vídeo ({nome}).',
    'tut_t_uma': 'Uma só rifa no template',
    'tut_b_uma': 'Não precisa de desenhar a folha toda. No Canva, crie uma página com o tamanho da rifa («Tamanho personalizado», por exemplo 19 × 5,5 cm) e escreva só um número de exemplo, 0001 (no talão e na parte principal, ou só num sítio).\n\nAo escolher esse PDF, o programa vê que tem uma só rifa e mostra «{papel}», «{margem}» e «{porfolha}»: enche a folha com cópias da rifa, o máximo que couber (roda-as 90° se assim couberem mais), e numera-as por ordem. A pré-visualização mostra a folha tal como vai sair.\n\n• O papel (A4, A3, A5, Letter, Legal) e a margem (as impressoras não imprimem junto ao bordo) podem ser mudados.\n• Se a página do PDF for maior do que a rifa, o programa recorta a zona desenhada.\n• «{porfolha}» começa no máximo; pode pedir menos.\n• Se couberem muitas rifas (mais de 24), o programa avisa: ficam pequenas e difíceis de recortar.\n• Se o seu PDF já tiver várias rifas por página (0001, 0002, …), tudo funciona como antes.',
    'tut_video': 'Prefere ver em vídeo? Abra o menu «{ajuda}» › «{video}».',
    'limpar': 'Limpar tudo',
    'tut_limpar': 'Quando acabar, «{limpar}» (ou menu «{ficheiro}» › «{limpar}») deixa tudo limpo — template, algarismos, pasta, nome, números e pré-visualização — para começar outra rifa.',
}

# --- interface web (src/web)
T.update({
    'web_descarregar': 'Descarregar',
    'web_senha': 'Palavra-passe',
    'web_entrar': 'Entrar',
    'web_senha_errada': 'Palavra-passe errada.',
    'web_demasiado_grande': 'O ficheiro é maior do que o limite ({mb} MB).',
    'web_ocupado': 'Já há uma geração em curso. Tente de novo daqui a pouco.',
    'web_voltar': 'Voltar',
    'web_ficheiros_gerados': 'PDFs gerados',
    'web_nova_janela': 'Abrir noutra janela',
    'web_tema_auto': 'Automático',
})
T.update({'web_demasiados': 'No máximo {max} números por pedido.'})
