# Changelog (English summary)

Translated summary of `../CHANGELOG.md`: same versions, sections and items, shorter. The full text is in Portuguese.

## 3.32.0 — 2026-11-13

### New
- **20 new templates in the gallery (24 in total):** Páscoa, Carnaval, Santos Populares, Coração, Praia, Halloween, Magusto, Futebol, Escola, Festival, Solidária, Bombeiros, Retro, Minimalista, Vindima, Arraial, Tesouro, Primavera, Inverno, Cinema. All drawn from scratch for this project, with a stub, on the site and in the Windows app (where the gallery becomes a drop-down list).

## 3.31.0 — 2026-11-13

### New
- **Template editor v2:** undo and redo (Ctrl+Z, Ctrl+Y), duplicate (Ctrl+D), change the drawing order, add your logo (PNG or JPG) and **share the design by link**: it is kept 90 days after its last access, without images and without data about who shares (it only appears when the service has a database). The Privacy Policy says so.
- **Windows app 2.5:** gets the template editor (Extras menu) and moves to Python 3.15.

### Improved
- The Changelog has a link to download the Windows app.

## 3.30.0 — 2026-11-12

### New
- **“How to” pages:** two written guides, “For schools” and “For associations” (links in the footer), with the step-by-step to run a raffle: design the ticket, one series per class or seller, print with cut marks, track sales and hold a verifiable draw. They are in all 18 languages and remind you to check with your local authority whether the raffle needs a licence.

## 3.29.0 — 2026-11-12

### Improved
- **Ads on the sides:** when ads are on (they are not for now), on wide screens they appear on both sides of the content, one on each side, fixed and without moving the page; on other screens there is a single block at the end of the page. They still never appear in the editor, in the generated files or in the Windows app.

## 3.28.0 — 2026-11-12

### New
- **Google ads (prepared, switched off):** the site can show a Google ads block (AdSense) at the end of the home page, the tutorial, “About”, the draw and the changelog. They never appear in the editor, in the generated files, in ticket verification, in the dashboard or in the Windows app, and in the European Economic Area and the United Kingdom only after you choose in Google's consent message. The Privacy Policy says so, in all 18 languages, when ads are on; for now they are off until the owner of the service configures them.

## 3.27.0 — 2026-11-12

### New
- **Template editor:** instead of using a Canva template, design the ticket on the site (the “Template editor” page, linked from step 1): add texts, rectangles, lines and the number 0001 (once, or twice if it has a stub), drag each element into place with the mouse or arrow keys, change colors, sizes and the background, and press “Use this template”. The screen uses the Vera font, the same as the PDF, so what you see is what you get; the draft stays only in the browser. Texts can't contain sequences like 0123, which the program would mistake for the ticket number (the screen and the server warn you).

## 3.26.0 — 2026-11-12

### New
- **Five new themes:** Halloween, Beach, Old newspaper, Green terminal and Circus poster, each with light and dark. The site now has 14 themes; the layout is the same in all of them (only colors and styling change).

## 3.25.0 — 2026-11-08

### New
- **One address per language for search engines:** each language has its own address (/en, /ja/tutorial…) with title, description and text in that language, and the site tells Google which versions are equivalent (hreflang). Portuguese stays at /. The chosen language now shows in the address bar.

## 3.24.1 — 2026-11-08

### Improved
- **Tick boxes aligned:** “One color per series” and the other tick boxes now sit next to their text instead of at the far end of the card.

## 3.24.0 — 2026-11-08

### Improved
- **Tutorial with screenshots of the site:** the basic tutorial topics now show the site itself, in all 18 languages, instead of the Windows app.

## 3.23.0 — 2026-11-08

### New
- **Tutorial and video for every feature:** the tutorial gets one topic per feature (series, list and control sheet, crop marks, gallery, your brand, QR, draw, save and share, install as app, themes), each with a short video recorded in the interface itself, in Portuguese and English.
- **Changelog, Terms, Privacy and Contact in 18 languages:** the text appears in the chosen language. The Changelog has a translated summary of each version (the full one is Portuguese); the legal texts are translations without native review and the Portuguese version prevails in case of difference.
- **Windows app 2.4** with what the site gained since 3.10: an “Extras” menu with series, prefixes and color per series, skipped numbers, number color, logo, crop marks, template gallery, verifiable draw and list (CSV) and control sheet export; plus automatic Christmas look in December. The verification QR and install as app stay on the site only.

## 3.22.0 — 2026-11-08

### Improved
- **Contrast of the 9 themes measured for real:** a browser test measures text against the real background pixels, in light and dark (WCAG AA), and what failed was fixed.
- The large decorative step numbers are no longer read by screen readers.

## 3.21.0 — 2026-11-08

### New
- **Verifiable draw** (“Draw” page): draws numbers from a range (with numbers to skip) so anyone can repeat it and get the same result, using a public seed. It runs in your browser and “Copy link” shares the same draw.
- The method is documented step by step, with a reference implementation that gives the same numbers as the site.

## 3.20.0 — 2026-11-08

### New
- **QR on every ticket:** a verification QR code in a corner of each ticket (single-ticket templates), with corner and size options. Scanning it opens a page confirming this service issued the code for that ticket. It is signed with a server-only key; nothing is stored in a database. It does not prove payment or a win.
- It only appears when the service owner sets the key. Requests with QR are capped at 10,000 numbers.

## 3.19.0 — 2026-11-08

### New
- **Your brand:** the number color (any template; a series color wins) and your association's **logo** on every ticket (PNG or JPG up to 2 MB, single-ticket templates), with corner and size (10 to 40 %). PNG keeps its transparency.
- The logo stays only in the session (erased with it and with “Clear everything”) and shows in the preview.

## 3.18.0 — 2026-11-08

### New
- **Template gallery:** pick one of four designs (Bosque, Quermesse, Natal and Gala), write title, organization, up to three prizes and the date, check the preview and press “Use this template”: template and digits are ready. Each design is a ticket with a stub.
- The designs are original to this project, in the free Vera font. The font only has the Latin alphabet: other letters show a warning.

## 3.17.0 — 2026-11-08

### New
- **Crop marks:** a checkbox in the sheet panel (single-ticket templates) draws short lines in the margins, extending each cutting line. It needs at least 3 mm of margin.
- The **stub** (the number twice on each ticket) already worked: now it is tested and documented.
- The **bleed** is already respected: if the Canva PDF has a TrimBox smaller than the page, the ticket is only what lies inside it.

## 3.16.0 — 2026-11-08

### New
- **Export the ticket list (CSV):** a file for Excel or Calc, one ticket per row (series, number and empty Name, Contact and Paid columns), respecting prefixes, series and skipped numbers.
- **Sales control sheet (PDF):** an A4 table to print and fill in by hand (36 tickets per page, with a “paid” box). In languages whose letters the PDF cannot write, the headings come out in English.
- Nothing is stored on the server: the list comes only from the form.

## 3.15.0 — 2026-11-08

### New
- **Series and prefixes:** text before the digits (A- gives A-0001). With several series separated by commas, each repeats the range and gets its own PDFs. A prefix takes letters, space, dot, hyphen and slash (up to 6 characters, no digits).
- **Skip numbers:** 13, 100-110 removes those numbers from the sequence (summary, files and verification count only what is printed).
- **A color for each series.**
- All of this also goes in “Copy link” and in the preview.

## 3.14.0 — 2026-11-08

### New
- **Install as an app (PWA):** install the site on your phone or computer; the app shell opens even offline (generating still needs the server). A simple service worker only stores the page, the app files and the interface texts, and never touches your files or generation requests.

## 3.13.0 — 2026-11-08

### New
- **Remember the digits file:** whoever comes back next year does not repeat it. It stays only in your browser (never on the server) and is reused with a new template; choosing another replaces it and “Clear everything” erases it.
- **Copy link:** a button that copies a link with the form values (from, to, mode, maximum per file, paper, margin and name). Whoever opens it sees the same values; files never go in the link.

## 3.12.0 — 2026-11-08

### New
- **Terms of use**, **Privacy policy** and **Contact** pages, linked in the footer. They are provisional versions, to be reviewed with legal support before the service charges anything.
- **Donate button** in the footer: it only appears when the owner sets the link. The contact e-mail and the responsible person's name also come from server configuration, never from the code.

## 3.11.0 — 2026-11-08

### New
- **Usage funnel** in the admin panel: how many events there are at each stage (session, template, digits, preview, generation, download) and what share of the previous stage reached the next. It shows where people give up. It counts events, not people.

## 3.10.0 — 2026-11-08

### New
- This page: the **Changelog**, with everything that changes, version by version.
- In **December** the automatic visual theme is **Christmas** (for anyone who never picked one). Choosing another theme is still remembered.

### Improved
- One dependency fewer on the server (`python-multipart` was no longer used: files arrive as a raw body).

## 3.9.0 — 2026-11-08

### New
- Layout designed for **large screens** (4K, ultra-wide) and **recent phones**: compact header and 44 px buttons.
- The preview shows an image when the browser cannot show PDFs inside the page (Chrome on Android).
- The admin panel records the **screen type** (class, size, family) without storing anything personal.
- The service calls itself every 10 minutes so it does not fall asleep.

## 3.8.0 — 2026-11-08

### New
- **Admin panel** (owner only, with a password) with charts and explanations of system and usage: aggregates only, never personal data.

## 3.7.0 — 2026-11-08

### New
- **SEO**: title, description and text per page, `robots.txt`, `sitemap.xml` and a real 404 for pages that do not exist.

## 3.6.0 — 2026-11-08

### Improved
- The site delivers **a single JavaScript file**, obfuscated and pre-compressed: what travels is much smaller than before.

## 3.5.0 — 2026-11-08

### New
- **Matrix Gamer** visual theme: falling green characters and neon glow.

## 3.4.0 — 2026-11-08

### Improved
- Styles move to **Sass** and ship as **a single CSS**. The page structure is the same in every theme: a theme only changes colors and formatting.

## 3.3.0 — 2026-11-07

### New
- **Visual themes**: Premiado (the new default look) and seven more (Quermesse, Arcade, Brutalista, Risografia, Janela 98, Gala and Natal), each with light and dark.
- New app icon.
