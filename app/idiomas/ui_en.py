T = {
    "m_ficheiro": "File", "m_ver": "View", "m_idioma": "Language", "m_ajuda": "Help",
    "mi_abrir_template": "Open template…", "mi_abrir_alg": "Choose digits file…",
    "mi_destino": "Choose destination folder…", "mi_sair": "Exit",
    "mi_zoom_mais": "Zoom in", "mi_zoom_menos": "Zoom out", "mi_ajustar": "Fit to window",
    "mi_expandir": "Expand preview", "mi_reduzir": "Shrink preview",
    "mi_tema": "Theme", "mi_tema_sistema": "Same as Windows", "mi_tema_claro": "Light", "mi_tema_escuro": "Dark",
    "mi_tutorial": "Step-by-step tutorial", "mi_sobre": "About…",
    "sobre_texto": ("{app}\nVersion {versao}\n\nCreates numbered raffle-ticket PDFs from a Canva template.\n\n"
                    "Built with pypdf, pypdfium2, Pillow and CustomTkinter (permissive licences)."),
    "tip_tema": "Switch between light and dark theme",
    "tut_titulo": "Tutorial", "tut_ant": "Previous", "tut_seg": "Next",
    "tut_t0": "Overview",
    "tut_b0": ("This program takes your raffle design made in Canva and creates print-ready PDFs with the numbers "
               "you want.\n\n"
               "There are only 4 steps, in the order shown on the left:\n\n"
               "• 1 – choose the template (the PDF from Canva);\n"
               "• 2 – choose the file with the digits 0 to 9;\n"
               "• 3 – say from which number to which number, and whether you want several PDFs or a single one;\n"
               "• 4 – choose the folder and type the name of the files.\n\n"
               "Then click “{previa}” to see a page and “{gerar}”. At the end every PDF is checked automatically."),
    "tut_b1": ("In Canva, design the raffle and write the example numbers 0001, 0002, 0003, … on the tickets "
               "(one per ticket). Each number appears twice: once on the stub and once on the main part of the "
               "ticket (see the picture).\n\n"
               "Download it as PDF and choose that file in step 1.\n\n"
               "• The program detects by itself how many tickets there are per page and the direction of the stub text.\n"
               "• The numbers must be text, not an image.\n"
               "• Other numbers in the design (year, phone…) are left untouched.\n"
               "• Only the first page of the PDF is used."),
    "tut_b3": ("• {de} / {ate}: the first and last number to generate (for example 1 to 1000).\n"
               "• {algarismos}: how many digits to write (4 → 0001). By default it is the one in the template; "
               "if you ask for more, the numbers shrink to fit.\n"
               "• {varios}: splits into files with at most the number of tickets you set (a multiple of the "
               "tickets per page).\n"
               "• {unico}: everything in one file.\n\n"
               "Below you see the summary: how many numbers, files and pages will be created."),
    "tut_b4": ("Choose the folder where the PDFs will be saved and type the name of the files (required; the "
               "program never suggests one). The files are saved as “NAME - 0001 - 0300.pdf”, "
               "“NAME - 0301 - 0600.pdf”, … or just “NAME - 0001 - 1000.pdf” with a single PDF.\n\n"
               "If files with those names already exist, the program asks before replacing them."),
    "tut_t5": "Preview and generate",
    "tut_b5": ("“{previa}” shows the 1st page with real numbers, so you can check the font, size and position "
               "before generating everything.\n\n"
               "In the viewer:\n"
               "• − / + or Ctrl + mouse wheel: zoom;\n"
               "• drag to move; double-click or “{ajustar}”: see the whole sheet;\n"
               "• the expand button gives the whole window to the preview; click again to go back;\n"
               "• the divider between the settings and the viewer can also be dragged.\n\n"
               "Click “{gerar}”. The bar shows the progress (you can cancel). At the end every PDF is checked "
               "automatically (pages and numbers) and the “{pasta}” button appears."),
    "tut_t6": "Tips and problems",
    "tut_b6": ("• “I did not find the example numbers”: in Canva the numbers must be text, written as 0001, 0002, … "
               "(each one twice).\n"
               "• The numbers come out in another font: the digits file must use exactly the same font as the "
               "template. Check it in the preview.\n"
               "• Numbers too small or odd: with PNG/JPG use a large image (≥ 100 px tall); PDF is always better.\n"
               "• “I could not save”: close the PDF if it is open in another program.\n"
               "• More digits than the design: the size shrinks automatically (a warning appears in the log).\n"
               "• You can change the language and the theme (light/dark) in the menus; the colours follow Windows."),
    'err_folha_varias': 'Only a template with a single ticket can be repeated on the sheet.',
    'err_rifa_grande': 'The ticket ({w} × {h} mm) does not fit on a {papel} sheet with {margem} mm margins.\n\nChoose a larger paper, reduce the margin or design a smaller ticket.',
    'log_folha': '{papel} sheet: {n} tickets per sheet ({w} × {h} mm each).',
    'aviso_muitas': '⚠ {n} tickets per sheet: they will be very small and hard to cut out. Check the ticket size.',
    'c1_ok_uma': '✔ Template with 1 ticket · sample number {primeiro}',
    'lay_info': 'The template has a single ticket: the program fills the sheet with copies, as many as fit.',
    'lay_papel': 'Paper',
    'lay_margem': 'Margin (mm)',
    'lay_por_folha': 'Tickets per sheet',
    'lay_resultado': 'Ticket of {w} × {h} mm → {n} per {papel} sheet (maximum {max})',
    'lay_recortada': ' · cropped to the artwork',
    'lay_rodadas': ' · {r} rotated 90°',
    'lay_acima': 'Only {max} fit on a sheet.',
    'conf_muitas': 'You are about to generate {n} tickets per sheet ({w} × {h} mm each). That is a lot: they will be small and hard to cut out.\n\nContinue?',
    'mi_video': 'Video tutorial',
    'video_falta': 'I could not find the video ({nome}).',
    'tut_t_uma': 'A single ticket in the template',
    'tut_b_uma': 'You do not need to design the whole sheet. In Canva, create a page the size of one ticket (“Custom size”, for example 19 × 5.5 cm) and write only one sample number, 0001 (on the stub and on the main part, or in just one place).\n\nWhen you choose that PDF, the program sees there is a single ticket and shows “{papel}”, “{margem}” and “{porfolha}”: it fills the sheet with copies of the ticket, as many as fit (rotating them 90° if more fit that way), and numbers them in order. The preview shows the sheet as it will be printed.\n\n• The paper (A4, A3, A5, Letter, Legal) and the margin (printers cannot print right to the edge) can be changed.\n• If the PDF page is bigger than the ticket, the program crops to the drawn area.\n• “{porfolha}” starts at the maximum; you can ask for fewer.\n• If many tickets fit (more than 24), the program warns you: they are small and hard to cut out.\n• If your PDF already has several tickets per page (0001, 0002, …), everything works as before.',
    'tut_video': 'Prefer to watch a video? Open the “{ajuda}” menu › “{video}”.',
    'limpar': 'Clear all',
    'tut_limpar': 'When it finishes, “{limpar}” (or the “{ficheiro}” menu › “{limpar}”) resets everything — template, digits, folder, name, numbers and preview — so you can start another raffle.',
}
