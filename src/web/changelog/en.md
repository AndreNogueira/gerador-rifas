# Changelog (English summary)

Translated summary of `../CHANGELOG.md`: same versions, sections and items, shorter. The full text is in Portuguese.

## 3.71.0 — 2026-11-20

### New
- **Numbered token vouchers** (in the price list, with a made-up currency; and “Extras → Price list… → Numbered vouchers…” in the Windows app): choose how many tokens each voucher is worth, the title and a note, see the voucher in the price list's design and create them. It continues in the raffle generator, which numbers the vouchers with series, verification QR codes and sheets ready to print.

## 3.70.0 — 2026-11-20

### New
- **Price list generator for events** (`/precario`, and “Extras → Price list…” in the Windows app): pick the occasion (the one for this time of year is suggested) and the items from a catalogue with pictures, type the prices in your country's currency or a made-up one (tokens…) and download the PDF (or an image) ready to print, in A5, A4 or A3 and with the gallery's 24 designs. There is also a new guide: “How to make a price list for an event”.

## 3.69.0 — 2026-11-19

### New
- **Brazilian Portuguese** (`/pt-br`): the site, the guides and the legal pages now also exist in Brazilian Portuguese, with its own vocabulary, a Privacy Policy adapted to Brazil's LGPD, and the language picked automatically when the browser is set to pt-BR. European Portuguese stays as it is, with no prefix in the address.

## 3.68.0 — 2026-11-19

### New
- **Three new guides, by topic** (not by audience): how to number raffle tickets, how to run a verifiable draw (it links to the «Draw» page) and how many tickets to make and at what price. Find them in «All guides» (`/como-fazer`), in 22 languages.

## 3.67.0 — 2026-11-19

### New
- **«How to» guides index** (`/como-fazer`): one page listing every guide with a short summary, and each guide now ends with links to the others. Also in the «Help» menu («All guides»).
- The guides and the index tell Google the path they sit on (Home › How to › guide), so search results can show it.

## 3.66.0 — 2026-11-19

### New
- **Invitation to leave a comment:** after downloading your raffles, a discreet notice appears (once per device) inviting you to leave a comment, anonymous if you like. You can dismiss it with “Not now”.

## 3.65.0 — 2026-11-19

### Improved
- **A lighter and safer site:** if you only generate raffles, you now download 24 % less code (the admin panel, the template editor and the draw page only load when you open them). The site also now sends security headers and answers link checkers and share previews.

## 3.64.0 — 2026-11-19

### New
- **Weekly backup of the admin panel data:** every Monday the service saves, in the same provider's storage as the database, a copy of the history, goals, action log, comments and SEO texts (last 8 weeks), with a script to restore it.

## 3.63.0 — 2026-11-19

### New
- **Real site performance in the statistics:** the admin panel shows, per day, how long the page takes to appear, how much the content moves and how long it takes to respond to a click, measured in visitors' browsers (mobile and desktop). Just three anonymous numbers per visit; the Privacy policy was updated.

## 3.62.0 — 2026-11-19

### New
- **Visit sources in the statistics:** the admin panel now shows where visits come from, in general categories (search, social networks, e-mail, other sites or direct) and by campaign (utm_source), to measure a promotion. The address of the page of origin and the IP are never stored; the Privacy policy was updated.

## 3.61.0 — 2026-11-19

### New
- **Action log in the admin panel:** who did what and when in the panel is kept for 400 days (logins, comments deleted or hidden, API keys, SEO texts, goals), with no visitor data or passwords.

## 3.60.0 — 2026-11-19

### New
- **Daily goals in the admin panel:** the owner sets a per-day target (sessions, generations, numbers generated, downloads…) and sees whether the last day met it, the 7-day average and on how many of those days it was reached; the daily e-mail report has the same section.

## 3.59.0 — 2026-11-19

### New
- **Comment status in the admin panel:** the owner can mark each comment as read, favourite or hidden (a hidden comment disappears from the public page but is not lost), filter by status and see how many are unread.

## 3.58.0 — 2026-11-19

### New
- **Free-hosting quotas in the admin panel:** it shows how many of the 750 monthly Render hours the service has used (with a projection to the end of the month) and how much space the database takes on Neon's free plan, with a warning in the daily e-mail report before the quotas run out.

## 3.57.0 — 2026-11-19

### New
- **Version markers on the admin panel charts:** each daily chart flags the day a new app version arrived (and the daily report says which), so a rise in errors or response time can be tied to the update that caused it.

## 3.56.0 — 2026-11-19

### New
- **Weekly and monthly e-mail summary for the site owner:** on Mondays the week's summary arrives and on the 1st the month's, with totals compared with the previous period and a thumbnail of each day. They read from the permanent history. Counts only.

## 3.55.0 — 2026-11-19

### New
- **Instant e-mail alerts for the site owner:** if there is a run of server errors, engine restarts, memory near the limit or the database not responding, a warning arrives right away (without waiting for the daily report and without repeating for 6 hours). Counts only.

## 3.54.0 — 2026-11-19

### New
- **Permanent history in the admin panel:** a summary of each day is saved after midnight, so the daily evolution now shows months and up to 2 years (before, only 90 days). Counts only, like the rest of the panel.

## 3.53.0 — 2026-11-19

### New
- **Daily e-mail report for the site owner:** every day, just after midnight, an e-mail arrives with everything recorded during the day that just ended (usage, audience, errors and server resources), compared with the average of the previous 7 days, so the app can be followed without opening the admin panel. Counts only: never visitor data.

## 3.52.0 — 2026-11-19

### Improved
- **Comments without an IP address:** instead of the IP, only the country the comment was sent from is stored (only the site owner sees it). The IP address is no longer stored: those of earlier comments were deleted, and the Privacy policy was updated.

## 3.51.0 — 2026-11-19

### New
- **Comments:** a “Comments” page where everyone can see what other people think of the generator, and a page to leave yours: you can stay anonymous or show a name (without a name, “Visitor no. …” appears). Your IP address is kept only for the site owner, to stop abuse, is never shown and is deleted after 90 days.
- **Report a problem:** a new page where you describe a bug and, when you press “Open”, it is created directly on the project's GitHub, no account needed (your IP is not sent and the browser's technical information is only included if you add it).
- Both pages and the “Comments” and “Report a problem” buttons are in plain view in the header, the menu and the footer; the Privacy policy (22 languages) explains what is stored.

## 3.50.0 — 2026-11-18

### Improved
- **A header that adapts to the screen:** all options sit on the right in a single row with no gaps, and as the screen shrinks they move one by one into a “burger” menu (the light/dark mode and the look first, the donation button last). On phones only the app name and the menu button remain; the menu opens with the pages, help, sharing and settings.

## 3.49.0 — 2026-11-18

### New
- **Dashboard with day-by-day evolution:** a new “Daily evolution” view shows, over up to 90 days, everything the server stores in its database (sessions, generations, numbers generated, languages, countries, looks, gallery, editor, API, requests, response times, CPU and memory…), with the trend of each indicator and a CSV download of it all. It is an owner-dashboard feature: visitors will not notice any difference.

## 3.48.0 — 2026-11-18

### Improved
- **“Help” menu in the header:** the tutorial, the video and the “How to” guides now share a single tab, “Help”. The header is shorter and the app name always shows in full on one line, in any language and screen size (it used to be cut off or split in two lines).

## 3.47.0 — 2026-11-15

### Improved
- **Template gallery:** the design list is no longer cut off or misplaced in some themes; each prize has its number; every text box shows its character limit (for example 12/50); and the “Use this template” button no longer sits right against the last box.
- **Draw date in its own calendar:** instead of the browser's field (which showed “dd/mm/yyyy” and a picker in a different language from the site), there is a calendar in all 22 languages, with months and weekdays in the chosen language, the date written the way that language writes it, the right first day of the week and “Today” and “Clear” buttons. It works with the keyboard (arrows, Page Up/Down, Home/End, Enter and Esc).
- **A fuller “About”:** the text was rewritten, in all 22 languages, and explains who the generator is for, what it does, what to do after printing, how it protects privacy and where it can be used.

## 3.46.0 — 2026-11-15

### Improved
- **Donation button easier to see:** when the service has a donation link, the button now appears in the header (next to «Share») and, after generating the files, with a short invitation. It is still in the footer too.

## 3.45.0 — 2026-11-14

### Improved
- **Template gallery on a single line:** the 24 designs are now picked from a one-line box where each option shows a mini drawing of the template, instead of a long list of buttons. It works with the mouse, touch and keyboard (arrows, Home/End, a letter, Enter and Esc).

## 3.44.0 — 2026-11-14

### Improved
- **Privacy:** usage counts now include the visit's country (only the code, deduced by the hosting network; the IP address is still not stored). The Privacy policy explains it in all 22 languages.

## 3.43.1 — 2026-11-14

### Improved
- **Cleaner footer:** the “How to” guides now appear only in the header group; they no longer repeat at the bottom of the page.

## 3.43.0 — 2026-11-14

### Improved
- **Draw date in a calendar:** in the template gallery you pick the date in a calendar and then how it appears on the ticket (31/12/2026, 31 Dec 2026, December 31, 2026 or with the weekday), written in the site's language. You can still type it by hand, now up to 60 characters.
- **Wider text:** text pages (guides, tutorial, terms…) now use the full width of the page, with fewer lines and paragraphs.

## 3.42.0 — 2026-11-14

### Improved
- **Header:** the new “How to” group, next to the tutorial, gathers the guides (schools, associations, clubs, firefighters, neighbourhood parties and parishes). The “Share” button moved from the footer to the header, highlighted, and its list shows the WhatsApp, Telegram, Facebook, e-mail and “Copy link” icons.

## 3.41.0 — 2026-11-14

### Improved
- **Automatic preview:** when you change the template, the digits, the logo or any field that alters the final page (numbers, digits, sheet, series, colours, QR…), the preview with real numbers refreshes by itself, without pressing “Preview”. If something is wrong, the reason shows next to the viewer, with no pop-ups.

## 3.40.0 — 2026-11-14

### New
- **3 to 10 prizes in the gallery:** in all 24 gallery designs you choose how many prizes the ticket has (3 to 10; it used to be 3 at most). From 6 on they go into two columns. Also in the Windows app.

## 3.39.0 — 2026-11-13

### New
- **Windows app 2.7:** the gallery and the template editor now accept extended Latin, Vietnamese, Greek, Cyrillic, Chinese, Japanese and Korean, like the site since 3.37 (Hindi, Arabic and Hebrew are still missing). Download it from the Changelog page.

## 3.38.0 — 2026-11-13

### New
- **“Share” button:** in the footer and, after generating the files, on the delivery card. It opens a short list (your phone's or computer's share sheet, WhatsApp, Telegram, Facebook, e-mail and “Copy link”) to let other associations, schools and festival committees know about the generator. The links carry only the site address in the language you are using: no tracking and nothing stored. It has a tutorial topic and a video.

## 3.37.0 — 2026-11-13

### New
- **More letters in the gallery and the template editor:** texts can now use extended Latin (Polish, Czech, Romanian, Turkish…), **Vietnamese, Greek, Cyrillic (Russian, Ukrainian)**, **Chinese, Japanese and Korean**. Hindi, Arabic and Hebrew are still missing (they need a writing technology the PDF generator lacks) and show a warning instead of a broken image. In the PDFs only the text typed by the user changes; what already came out the same stays the same.

## 3.36.0 — 2026-11-13

### New
- **“How to” guide for parishes:** “For parishes” (link in the footer), with the step-by-step to run a raffle for your parish: patron saint feasts, fairs, repairs, Christmas hampers and catechism. It is in all 22 languages and reminds you to check with your local authority whether the raffle needs a licence.

## 3.35.0 — 2026-11-13

### New
- **Windows app 2.6:** the “Extras” menu gains “Save request…” and “Open request…” (a .rifas file with the numbers, the name, the series, the colours and the crop marks, with no template or paths), the template editor can add images (PNG or JPG) and “View → Visual” goes from 2 to the site's 14 themes (colours only). It also brings what came since 2.4: the editor, the gallery's 24 designs and the 22 languages.

## 3.34.0 — 2026-11-13

### New
- **Three new “How to” guides:** “For clubs”, “For fire brigades” and “For neighbourhood parties” (links in the footer), with the step-by-step to run a raffle in each case. They are in all 22 languages and remind you to check with your local authority whether the raffle needs a licence.

## 3.33.0 — 2026-11-13

### New
- **Public API for batches** (`/api/v1`, with Swagger at `/api/v1/docs`): lets other programs generate several raffle jobs from a single template, with a key, daily quotas and limits. People using the site always go first.
- **Four new languages:** Catalan, Ukrainian, Indonesian and Vietnamese. The site and the Windows app now speak 22 languages, with tutorial, terms, privacy, how-to guides and screenshots.
- **Search-engine texts editable per language:** the owner edits the titles, descriptions and guides of each language in the admin panel, stored in the database, with no new deploy.

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
