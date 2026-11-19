# Changelog (shrnutí česky)

Přeložené shrnutí `../CHANGELOG.md`: stejné verze, oddíly a body, kratší. Úplný text je v portugalštině.

## 3.54.0 — 2026-11-19

### Novinky
- **Trvalá historie v administračním panelu:** po půlnoci se uloží souhrn každého dne, takže denní vývoj nyní ukazuje měsíce a až 2 roky (dříve jen 90 dnů). Pouze počty, jako zbytek panelu.

## 3.53.0 — 2026-11-19

### Novinky
- **Denní e-mailová zpráva pro provozovatele webu:** každý den těsně po půlnoci přijde e-mail se vším, co se zaznamenalo za právě skončený den (využití, publikum, chyby a zdroje serveru), porovnané s průměrem předchozích 7 dnů, aby šlo aplikaci sledovat bez otevření panelu. Pouze počty: nikdy údaje návštěvníků.

## 3.52.0 — 2026-11-19

### Vylepšeno
- **Komentáře bez IP adresy:** místo IP se ukládá jen země, ze které byl komentář odeslán (vidí ji pouze provozovatel webu). IP adresa se už neukládá: ty u dřívějších komentářů byly smazány a Zásady ochrany soukromí byly aktualizovány.

## 3.51.0 — 2026-11-19

### Novinky
- **Komentáře:** stránka «Komentáře», kde každý vidí, co si ostatní o generátoru myslí, a stránka pro vlastní komentář: můžete zůstat anonymní nebo ukázat jméno (bez jména se zobrazí «Návštěvník č. …»). IP adresa se ukládá jen pro provozovatele webu, proti zneužití, nikdy se nezobrazuje a po 90 dnech se maže.
- **Nahlásit problém:** nová stránka, kde popíšete chybu; po stisknutí «Otevřít» se vytvoří přímo na GitHubu projektu, bez účtu (vaše IP se neodesílá a technické údaje prohlížeče jen pokud je přidáte).
- Obě stránky a tlačítka «Komentáře» a «Nahlásit problém» jsou dobře vidět v záhlaví, nabídce i patičce; Zásady ochrany soukromí (22 jazyků) vysvětlují, co se ukládá.

## 3.50.0 — 2026-11-18

### Vylepšeno
- **Záhlaví, které se přizpůsobí obrazovce:** všechny volby jsou zarovnané vpravo v jednom řádku bez mezer a jak se obrazovka zmenšuje, přesouvají se jedna po druhé do «hamburgerové» nabídky (nejdřív světlý/tmavý režim a vzhled, nakonec dar). Na telefonu zůstane jen název aplikace a tlačítko nabídky, která otevře stránky, nápovědu, sdílení a nastavení.

## 3.49.0 — 2026-11-18

### Novinky
- **Panel s vývojem den po dni:** nový pohled «Denní vývoj» ukazuje až za 90 dní vše, co server ukládá do databáze (relace, generování, vygenerovaná čísla, jazyky, země, vzhledy, galerii, editor, API, požadavky, doby odezvy, CPU a paměť…), s trendem každého ukazatele a stažením všeho do CSV. Je to funkce panelu majitele: návštěvníci žádný rozdíl nepoznají.

## 3.48.0 — 2026-11-18

### Vylepšeno
- **Nabídka «Nápověda» v záhlaví:** návod, video a průvodci «Jak na to» jsou nyní na jedné záložce, «Nápověda». Záhlaví je kratší a název aplikace je vždy vidět celý na jednom řádku, v každém jazyce i na každé velikosti obrazovky.

## 3.47.0 — 2026-11-15

### Vylepšeno
- **Galerie šablon:** seznam návrhů už se v některých motivech neořezává ani neposouvá; každá cena má své číslo; každé textové pole ukazuje limit znaků (například 12/50); a tlačítko «Použít tuto šablonu» už není nalepené na poslední pole.
- **Datum losování ve vlastním kalendáři:** místo pole prohlížeče (které ukazovalo «dd.mm.rrrr» a výběr v jiném jazyce, než má web) je tu kalendář ve 22 jazycích s měsíci a dny v týdnu ve zvoleném jazyce, datem zapsaným tak, jak ho tento jazyk píše, správným prvním dnem týdne a tlačítky «Dnes» a «Vymazat». Funguje s klávesnicí (šipky, Page Up/Down, Home/End, Enter a Esc).
- **Úplnější «O programu»:** text byl přepsán ve 22 jazycích a vysvětluje, pro koho generátor je, co dělá, co dělat po tisku, jak chrání soukromí a kde se dá používat.

## 3.46.0 — 2026-11-15

### Vylepšeno
- **Dar je lépe vidět:** má-li služba odkaz na dary, tlačítko se nyní zobrazuje v záhlaví (vedle «Sdílet») a po vytvoření souborů s krátkou výzvou. Zůstává i v patičce.

## 3.45.0 — 2026-11-14

### Vylepšeno
- **Galerie šablon na jednom řádku:** 24 návrhů se nyní vybírá v jednořádkovém poli, kde každá volba ukazuje miniaturu šablony, místo dlouhého seznamu tlačítek. Funguje s myší, dotykem i klávesnicí (šipky, Home/End, písmeno, Enter a Esc).

## 3.44.0 — 2026-11-14

### Vylepšeno
- **Soukromí:** počty využití nově zahrnují zemi návštěvy (jen kód, který odvodí síť hostingu; IP adresa se stále neukládá). Zásady ochrany soukromí to vysvětlují ve všech 22 jazycích.

## 3.43.1 — 2026-11-14

### Vylepšeno
- **Čistší zápatí:** průvodci «Jak na to» se nyní zobrazují jen ve skupině v záhlaví; už se neopakují dole na stránce.

## 3.43.0 — 2026-11-14

### Vylepšeno
- **Datum losování v kalendáři:** v galerii šablon vyberete datum v kalendáři a pak jak se zobrazí na losu (31. 12. 2026, 31. 12. 2026 zkráceně, 31. prosince 2026 nebo s dnem v týdnu), v jazyce stránky. Pořád ho lze napsat ručně, nově až 60 znaků.
- **Širší texty:** textové stránky (průvodci, návod, podmínky…) nově využívají celou šířku stránky, s méně řádky a odstavci.

## 3.42.0 — 2026-11-14

### Vylepšeno
- **Záhlaví:** nová skupina «Jak na to», vedle návodu, sdružuje průvodce (školy, spolky, kluby, hasiči, sousedské slavnosti a farnosti). Tlačítko «Sdílet» se přesunulo ze zápatí do záhlaví, zvýrazněné, a jeho seznam ukazuje ikony WhatsAppu, Telegramu, Facebooku, e-mailu a «Kopírovat odkaz».

## 3.41.0 — 2026-11-14

### Vylepšeno
- **Automatický náhled:** když změníte šablonu, číslice, logo nebo jakékoli pole, které mění výslednou stránku (čísla, číslice, arch, série, barvy, QR…), náhled se skutečnými čísly se obnoví sám, bez klepnutí na „Náhled“. Když je něco špatně, důvod se zobrazí vedle prohlížeče, bez oken.

## 3.40.0 — 2026-11-14

### Novinky
- **3 až 10 cen v galerii:** u všech 24 návrhů v galerii si vyberete, kolik cen los má (3 až 10; dříve nejvýše 3). Od 6 se řadí do dvou sloupců. Také v aplikaci pro Windows.

## 3.39.0 — 2026-11-13

### Novinky
- **Aplikace pro Windows 2.7:** galerie a editor šablon nově přijímají rozšířenou latinku, vietnamštinu, řečtinu, cyrilici, čínštinu, japonštinu a korejštinu, stejně jako web od verze 3.37 (hindština, arabština a hebrejština zatím chybí). Ke stažení na stránce Changelog.

## 3.38.0 — 2026-11-13

### Novinky
- **Tlačítko «Sdílet»:** v patičce a po vygenerování souborů na kartě s výsledkem. Otevře krátký seznam (sdílení telefonu nebo počítače, WhatsApp, Telegram, Facebook, e-mail a «Kopírovat odkaz»), aby o generátoru věděly další spolky, školy a výbory slavností. Odkazy obsahují jen adresu webu v použitém jazyce: žádné sledování a nic se neukládá. Má téma v návodu a video.

## 3.37.0 — 2026-11-13

### Novinky
- **Více písmen v galerii a v editoru šablon:** texty mohou nově obsahovat rozšířenou latinku (polštinu, češtinu, rumunštinu, turečtinu…), **vietnamštinu, řečtinu, cyrilici (ruštinu, ukrajinštinu)**, **čínštinu, japonštinu a korejštinu**. Hindština, arabština a hebrejština zatím chybí (potřebují techniku psaní, kterou generátor PDF nemá) a místo rozbitého obrázku ukážou varování. V PDF se mění jen napsaný text; co vycházelo stejně, vychází stejně.

## 3.36.0 — 2026-11-13

### Novinky
- **Návod «Jak na to» pro farnosti:** «Pro farnosti» (odkaz v patičce), s postupem krok za krokem, jak uspořádat farní tombolu: poutě, farní dny, opravy, vánoční balíčky a náboženství. Je ve všech 22 jazycích a připomíná, že se na obecním úřadě má ověřit, zda tombola vyžaduje povolení.

## 3.35.0 — 2026-11-13

### Novinky
- **Aplikace pro Windows 2.6:** nabídka «Extras» získává «Uložit zakázku…» a «Otevřít zakázku…» (soubor .rifas s čísly, názvem, sériemi, barvami a ořezovými značkami, bez šablony a cest), editor šablon umí přidávat obrázky (PNG nebo JPG) a «Zobrazení → Vzhled» se rozšiřuje ze 2 na 14 motivů webu (jen barvy). Přináší i to, co přišlo od verze 2.4: editor, 24 vzorů v galerii a 22 jazyků.

## 3.34.0 — 2026-11-13

### Novinky
- **Tři nové návody „Jak na to“:** „Pro kluby“, „Pro hasiče“ a „Pro slavnosti“ (odkazy v patičce), vždy s postupem krok za krokem, jak uspořádat tombolu. Jsou ve všech 22 jazycích a připomínají, že se na obecním úřadě má ověřit, zda tombola vyžaduje povolení.

## 3.33.0 — 2026-11-13

### Novinky
- **Veřejné API pro dávky** (`/api/v1`, se Swaggerem na `/api/v1/docs`): umožňuje jiným programům vytvářet více zakázek na losy z jedné šablony, s klíčem, denními kvótami a limity. Uživatelé webu mají vždy přednost.
- **Čtyři nové jazyky:** katalánština, ukrajinština, indonéština a vietnamština. Web i aplikace pro Windows nyní mluví 22 jazyky, s návodem, podmínkami, soukromím, průvodci a snímky obrazovky.
- **Texty pro vyhledávače upravitelné pro každý jazyk:** majitel upravuje v administračním panelu názvy, popisy a průvodce každého jazyka, uložené v databázi a bez nového nasazení.

## 3.32.0 — 2026-11-13

### Novinky
- **20 nových šablon v galerii (celkem 24):** Páscoa, Carnaval, Santos Populares, Coração, Praia, Halloween, Magusto, Futebol, Escola, Festival, Solidária, Bombeiros, Retro, Minimalista, Vindima, Arraial, Tesouro, Primavera, Inverno, Cinema. Všechny nakreslené od nuly pro tento projekt, s útržkem, na webu i v aplikaci pro Windows (kde se galerie mění na rozbalovací seznam).

## 3.31.0 — 2026-11-13

### Novinky
- **Editor šablon v2:** zpět a znovu (Ctrl+Z, Ctrl+Y), duplikovat (Ctrl+D), změna pořadí kreslení, přidání loga (PNG nebo JPG) a **sdílení návrhu odkazem**: uchovává se 90 dní od posledního přístupu, bez obrázků a bez údajů o tom, kdo sdílí (zobrazí se jen tehdy, když služba má databázi). Zásady ochrany soukromí to uvádějí.
- **Aplikace pro Windows 2.5:** dostává editor šablon (nabídka Extra) a přechází na Python 3.15.

### Vylepšeno
- Changelog má odkaz ke stažení aplikace pro Windows.

## 3.30.0 — 2026-11-12

### Novinky
- **Stránky „Jak na to“:** dva psané návody, „Pro školy“ a „Pro spolky“ (odkazy v patičce), s postupem krok za krokem, jak uspořádat tombolu: navrhnout los, série pro třídu nebo prodejce, tisk s ořezovými značkami, hlídání prodeje a ověřitelné losování. Jsou ve všech 18 jazycích a připomínají ověřit na obecním úřadě, zda tombola vyžaduje povolení.

## 3.29.0 — 2026-11-12

### Vylepšeno
- **Reklamy po stranách:** když jsou reklamy zapnuté (zatím nejsou), na širokých obrazovkách se zobrazují po obou stranách obsahu, po jedné z každé strany, pevné a bez posouvání stránky; na ostatních obrazovkách je jeden blok na konci stránky. Stále se nezobrazují v editoru, ve vytvořených souborech ani v aplikaci pro Windows.

## 3.28.0 — 2026-11-12

### Novinky
- **Reklamy Google (připravené, vypnuté):** web může na konci úvodní stránky, návodu, „O programu“, losování a changelogu zobrazit blok reklam Google (AdSense). Nikdy se nezobrazují v editoru, ve vytvořených souborech, při ověřování losů, v panelu ani v aplikaci pro Windows a v Evropském hospodářském prostoru a ve Spojeném království až po vaší volbě ve zprávě o souhlasu od Google. Zásady ochrany soukromí to ve všech 18 jazycích uvádějí, když jsou reklamy zapnuté; zatím jsou vypnuté, dokud je provozovatel služby nenastaví.

## 3.27.0 — 2026-11-12

### Novinky
- **Editor šablon:** místo šablony z Canvy navrhněte los na webu (stránka „Editor šablon“, odkaz od kroku 1): přidejte texty, obdélníky, čáry a číslo 0001 (jednou, nebo dvakrát s útržkem), každý prvek přetáhněte myší nebo šipkami, změňte barvy, velikosti a pozadí a klikněte na „Použít tuto šablonu“. Obrazovka používá písmo Vera jako PDF, takže co vidíte, to dostanete; koncept zůstává jen v prohlížeči. Texty nesmí obsahovat řady jako 0123, které by program zaměnil s číslem losu (upozorní obrazovka i server).

## 3.26.0 — 2026-11-12

### Novinky
- **Pět nových motivů:** Halloween, Pláž, Staré noviny, Zelený terminál a Cirkusový plakát, každý ve světlé i tmavé verzi. Web má nyní 14 motivů; rozvržení je ve všech stejné (mění se jen barvy a vzhled).

## 3.25.0 — 2026-11-08

### Novinky
- **Jedna adresa pro každý jazyk pro vyhledávače:** každý jazyk má vlastní adresu (/en, /ja/tutorial…) s názvem, popisem a textem v tomto jazyce a web sděluje Googlu, které verze jsou rovnocenné (hreflang). Portugalština zůstává na /. Zvolený jazyk je nyní vidět v adresním řádku.

## 3.24.1 — 2026-11-08

### Vylepšeno
- **Zarovnaná zaškrtávací políčka:** „Jedna barva pro každou sérii“ a další políčka jsou nyní vedle textu, ne na druhém konci karty.

## 3.24.0 — 2026-11-08

### Vylepšeno
- **Návod se snímky obrazovky webu:** základní témata návodu nyní ukazují samotný web, ve všech 18 jazycích, místo aplikace pro Windows.

## 3.23.0 — 2026-11-08

### Novinky
- **Návod a video ke každé funkci:** návod má téma pro každou funkci (řady, seznam a kontrolní list, ořezové značky, galerie, vlastní značka, QR, losování, ukládání a sdílení, instalace jako aplikace, motivy), každé s krátkým videem nahraným přímo v rozhraní, v portugalštině a angličtině.
- **Changelog, Podmínky, Soukromí a Kontakt v 18 jazycích:** text se zobrazí ve zvoleném jazyce. Changelog má přeložené shrnutí každé verze (úplný je portugalský); právní texty jsou překlady bez kontroly rodilými mluvčími a při rozdílech platí portugalská verze.
- **Aplikace pro Windows 2.4** s tím, co web získal od verze 3.10: nabídka „Doplňky“ s řadami, předponami a barvou řady, vynechanými čísly, barvou čísel, logem, ořezovými značkami, galerií šablon, ověřitelným losováním a exportem seznamu (CSV) a kontrolního listu; a automatický vánoční vzhled v prosinci. Ověřovací QR a instalace jako aplikace zůstávají jen na webu.

## 3.22.0 — 2026-11-08

### Vylepšeno
- **Kontrast 9 motivů skutečně změřen:** test v prohlížeči měří text proti skutečným pixelům pozadí, ve světlém i tmavém režimu (WCAG AA), a co neprošlo, bylo opraveno.
- Velká dekorativní čísla kroků už čtečky obrazovky nečtou.

## 3.21.0 — 2026-11-08

### Novinky
- **Ověřitelné losování** (stránka „Losování“): losuje čísla z rozsahu (s vynechanými čísly) tak, aby je kdokoli mohl zopakovat a získat stejný výsledek, s veřejným semínkem. Probíhá v prohlížeči a „Kopírovat odkaz“ sdílí totéž losování.
- Metoda je popsána krok za krokem, s referenční implementací, která dává stejná čísla jako web.

## 3.20.0 — 2026-11-08

### Novinky
- **QR na každém losu:** ověřovací QR kód v rohu každého losu (šablony s jedním losem), s volbou rohu a velikosti. Po naskenování se otevře stránka potvrzující, že tato služba vydala kód pro daný los. Podepsáno klíčem, který má jen server; bez databáze. Nedokazuje platbu ani výhru.
- Objeví se, jen když majitel služby nastaví klíč. Zakázky s QR mají strop 10 000 čísel.

## 3.19.0 — 2026-11-08

### Novinky
- **Vlastní značka:** barva čísel (jakákoli šablona; barva řady má přednost) a **logo** spolku na každém losu (PNG nebo JPG do 2 MB, šablony s jedním losem), s rohem a velikostí (10 až 40 %). PNG zachová průhlednost.
- Logo zůstává jen v relaci (smaže se s ní i příkazem „Vymazat vše“) a vidíte ho v náhledu.

## 3.18.0 — 2026-11-08

### Novinky
- **Galerie šablon:** vyberte jeden ze čtyř návrhů (Bosque, Quermesse, Natal a Gala), napište název, organizaci, až tři ceny a datum, prohlédněte si náhled a klikněte na „Použít tuto šablonu“: šablona i číslice jsou hotové. Každý návrh je los s útržkem.
- Návrhy jsou původní pro tento projekt, ve volném písmu Vera. Písmo má jen latinku: u jiných písmen se zobrazí upozornění.

## 3.17.0 — 2026-11-08

### Novinky
- **Ořezové značky:** zaškrtávací pole v panelu listu (šablony s jedním losem) nakreslí krátké čárky na okrajích, které prodlužují každou řeznou linii. Vyžaduje alespoň 3 mm okraj.
- **Útržek** (číslo dvakrát na každém losu) fungoval už dřív: nyní je otestován a zdokumentován.
- **Spadávka** se už respektuje: má-li PDF z Canvy menší TrimBox než stránka, los je jen to, co leží uvnitř.

## 3.16.0 — 2026-11-08

### Novinky
- **Export seznamu losů (CSV):** soubor pro Excel nebo Calc, jeden los na řádek (řada, číslo a prázdné sloupce Jméno, Kontakt, Zaplaceno), s předponami, řadami a vynechanými čísly.
- **Kontrolní list prodeje (PDF):** tabulka A4 k vytištění a ručnímu vyplnění (36 losů na stránku, s polem „zaplaceno“). V jazycích, jejichž písmena PDF nenapíše, jsou záhlaví anglicky.
- Na serveru se nic neukládá: seznam vzniká jen z formuláře.

## 3.15.0 — 2026-11-08

### Novinky
- **Řady a předpony:** text před číslicemi (A- dá A-0001). U více řad oddělených čárkami každá opakuje rozsah a má vlastní PDF. Předpona smí obsahovat písmena, mezeru, tečku, pomlčku a lomítko (nejvýše 6 znaků, bez číslic).
- **Vynechání čísel:** 13, 100-110 odebere tato čísla z řady (souhrn, soubory i kontrola počítají jen to, co se tiskne).
- **Barva pro každou řadu.**
- To vše je také v „Kopírovat odkaz“ a v náhledu.

## 3.14.0 — 2026-11-08

### Novinky
- **Instalace jako aplikace (PWA):** nainstalujte web v telefonu nebo počítači; kostra aplikace se otevře i bez sítě (generování stále potřebuje server). Jednoduchý service worker ukládá jen stránku, soubory aplikace a texty rozhraní a nikdy se nedotkne vašich souborů ani požadavků na generování.

## 3.13.0 — 2026-11-08

### Novinky
- **Zapamatování souboru s číslicemi:** kdo se vrátí příští rok, nemusí ho opakovat. Zůstává jen ve vašem prohlížeči (nikdy na serveru) a použije se s novou šablonou; výběr jiného ho nahradí a „Vymazat vše“ ho smaže.
- **Kopírovat odkaz:** tlačítko, které zkopíruje odkaz s hodnotami formuláře (od, do, režim, maximum na soubor, papír, okraj a název). Kdo ho otevře, uvidí stejné hodnoty; soubory v odkazu nikdy nejsou.

## 3.12.0 — 2026-11-08

### Novinky
- Stránky **Podmínky použití**, **Zásady ochrany soukromí** a **Kontakt**, odkazované v patičce. Jsou to předběžné verze, které je třeba před zpoplatněním služby zkontrolovat s právní pomocí.
- **Tlačítko pro dary** v patičce: objeví se, jen když majitel nastaví odkaz. Kontaktní e-mail a jméno odpovědné osoby také pocházejí z konfigurace serveru, nikdy z kódu.

## 3.11.0 — 2026-11-08

### Novinky
- **Trychtýř používání** v administraci: kolik událostí je v každém kroku (relace, šablona, číslice, náhled, generování, stažení) a jaká část předchozího kroku došla k dalšímu. Ukazuje, kde lidé končí. Počítá události, ne osoby.

## 3.10.0 — 2026-11-08

### Novinky
- Tato stránka: **Changelog** se vším, co se mění, verze po verzi.
- V **prosinci** je automatickým motivem **Vánoce** (pro toho, kdo žádný nezvolil). Volba jiného motivu se dál pamatuje.

### Vylepšeno
- O jednu závislost méně na serveru (`python-multipart` se už nepoužíval: soubory přicházejí jako surové tělo).

## 3.9.0 — 2026-11-08

### Novinky
- Rozvržení pro **velké obrazovky** (4K, ultraširoké) a **nové telefony**: kompaktní záhlaví a tlačítka 44 px.
- Náhled ukazuje obrázek, když prohlížeč neumí zobrazit PDF na stránce (Chrome v Androidu).
- Administrace zaznamenává **typ obrazovky** (třída, velikost, rodina), aniž by ukládala cokoli osobního.
- Služba se sama volá každých 10 minut, aby neusnula.

## 3.8.0 — 2026-11-08

### Novinky
- **Administrace** (jen pro majitele, s heslem) s grafy a vysvětlením systému a používání: jen souhrny, nikdy osobní údaje.

## 3.7.0 — 2026-11-08

### Novinky
- **SEO**: název, popis a text pro každou stránku, `robots.txt`, `sitemap.xml` a skutečná chyba 404 u neexistujících stránek.

## 3.6.0 — 2026-11-08

### Vylepšeno
- Web dodává **jediný soubor JavaScriptu**, zakódovaný a předem zkomprimovaný: to, co se přenáší, je mnohem menší než dřív.

## 3.5.0 — 2026-11-08

### Novinky
- Motiv **Matrix Gamer**: déšť zelených znaků a neonová záře.

## 3.4.0 — 2026-11-08

### Vylepšeno
- Styly přecházejí na **Sass** a vycházejí jako **jediné CSS**. Struktura stránky je ve všech motivech stejná: motiv mění jen barvy a formátování.

## 3.3.0 — 2026-11-07

### Novinky
- **Motivy**: Premiado (nový výchozí vzhled) a sedm dalších (Quermesse, Arcade, Brutalista, Risografia, Janela 98, Gala a Natal), každý světlý i tmavý.
- Nová ikona aplikace.
