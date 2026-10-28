"""Bouwt de statische site in de map site/ uit data/inkopers.json.

Gebruik:  python3 tools/build.py
Pas data/inkopers.json aan en draai dit script opnieuw om de site bij te werken.
"""
import json
import shutil
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site"
DATA = json.loads((ROOT / "data" / "inkopers.json").read_text(encoding="utf-8"))

MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli",
           "augustus", "september", "oktober", "november", "december"]


def nl_datum(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} {MAANDEN[d.month - 1]} {d.year}"


GECONTROLEERD = nl_datum(DATA["gecontroleerd"])
SITE = "https://www.gadgetdeal.nl"
LAATST_BIJGEWERKT = "2026-10-28"

NAV = [
    ("/", "Telefoon verkopen"),
    ("/sim-only/", "Sim only"),
    ("/uitleg/", "Uitleg"),
    ("/hoe-wij-vergelijken/", "Hoe wij vergelijken"),
]


def page(path: str, title: str, description: str, body: str, scripts: str = "") -> None:
    nav = "".join(
        f'<a href="{href}"{" aria-current=\"page\"" if href == path else ""}>{label}</a>'
        for href, label in NAV
    )
    html = f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{SITE}{path}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:locale" content="nl_NL">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="/">Gadget<span>Deal</span></a>
    <nav class="site-nav" aria-label="Hoofdmenu">{nav}</nav>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p>GadgetDeal vergelijkt waar je je telefoon kunt verkopen. Via sommige links op deze site kunnen wij een vergoeding ontvangen, zonder extra kosten voor jou. <a href="/hoe-wij-vergelijken/">Zo werkt het</a>.</p>
    <nav aria-label="Overige pagina's">
      <a href="/hoe-wij-vergelijken/">Hoe wij vergelijken</a>
      <a href="/privacy/">Privacy</a>
      <a href="/contact/">Contact</a>
    </nav>
  </div>
</footer>
{scripts}
</body>
</html>
"""
    target = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")


MARK_TEXT = {"ja": "Ja", "nee": "Nee", "onbekend": "Niet vermeld"}


def mark(value: str) -> str:
    return f'<span class="mark {value}">{MARK_TEXT[value]}</span>'


def buyer_row(b: dict, group: str) -> str:
    link = b["affiliate_url"] or b["url"]
    rel = "sponsored noopener" if b["affiliate_url"] else "nofollow noopener"
    paid = '<span class="paid">Wij ontvangen commissie via deze link</span>' if b["affiliate_url"] else ""
    note = f"<small>{escape(b['notitie'])}</small>" if b["notitie"] else ""
    via = (' <small class="source">via <a href="https://nomophone.com/nl/guides/marche/waar-telefoon-verkopen-vergelijking" rel="nofollow noopener">NomoPhone</a></small>'
           if b.get("via") else "")
    return f"""<tr data-naam="{escape(b['naam'])}" data-group="{group}" data-geld="{str(b['geld']).lower()}" data-retour="{b['retour']}" data-kapot="{b['kapot']}">
  <th scope="row">{escape(b['naam'])}{note}</th>
  <td data-label="Uitbetaling">{escape(b['uitbetaling'])}</td>
  <td data-label="Termijn">{escape(b['termijn'])}</td>
  <td data-label="Gratis retour bij een lager bod">{mark(b['retour'])}</td>
  <td data-label="Kapotte toestellen">{mark(b['kapot'])}</td>
  <td data-label="Bron"><a class="source" href="{escape(b['bron'])}" rel="nofollow noopener">Bron</a>{via}</td>
  <td class="cta"><a class="go" href="{escape(link)}" rel="{rel}" target="_blank" aria-label="{escape(b['knop'])} bij {escape(b['naam'])}">{escape(b['knop'])}</a>{paid}</td>
</tr>"""


def home() -> None:
    geld = sorted([b for b in DATA["inkopers"] if b["geld"]], key=lambda b: b["naam"].lower())
    tegoed = sorted([b for b in DATA["inkopers"] if not b["geld"]], key=lambda b: b["naam"].lower())
    rows = (
        '<tr class="group-row" data-group="geld"><td colspan="7">Je krijgt geld</td></tr>'
        + "".join(buyer_row(b, "geld") for b in geld)
        + '<tr class="group-row" data-group="tegoed"><td colspan="7">Je krijgt tegoed, een cadeaubon of korting</td></tr>'
        + "".join(buyer_row(b, "tegoed") for b in tegoed)
    )
    total = len(DATA["inkopers"])
    body = f"""
<div class="wrap hero">
  <div>
    <h1>Waar verkoop je je oude telefoon?</h1>
    <p>Elke inkoper doet je een bod, maar de voorwaarden verschillen. Krijg je geld of een cadeaubon? Krijg je je telefoon gratis terug als ze na controle minder bieden?</p>
    <p>Hier zie je het naast elkaar voor {total} inkopers, met bij elke inkoper een link naar de bron. <a href="/hoe-wij-vergelijken/">Welke inkopers we opnemen</a></p>
  </div>
  <form class="label" id="filters" aria-describedby="count">
    <div class="label-head"><span>Wat vind jij belangrijk?</span><small>Vink aan om te filteren</small></div>
    <fieldset>
      <legend class="visually-hidden" style="position:absolute;left:-9999px">Filters</legend>
      <label class="check"><input type="checkbox" name="geld"><span><strong>Uitbetaling in geld</strong><span>Geen cadeaubon of korting op iets nieuws</span></span></label>
      <label class="check"><input type="checkbox" name="retour"><span><strong>Gratis terug bij een lager bod</strong><span>Als ze na controle minder bieden en jij nee zegt</span></span></label>
      <label class="check"><input type="checkbox" name="kapot"><span><strong>Mijn telefoon is kapot</strong><span>Alleen inkopers die kapotte toestellen kopen</span></span></label>
    </fieldset>
    <div class="label-foot"><output id="count" aria-live="polite">{total} inkopers</output><button type="button" id="reset">Filters wissen</button></div>
  </form>
</div>

<section class="wrap results" aria-labelledby="vergelijking">
  <h2 id="vergelijking">Inkopers vergeleken</h2>
  <p>Op alfabet, niet op hoeveel wij eraan verdienen. Prijzen tonen we nog niet: die hangen af van je model, opslag en de staat van je toestel. Vraag bij twee of drie inkopers een bod aan. Gecontroleerd op {GECONTROLEERD}.</p>
  <table class="buyers" id="buyers">
    <thead><tr><th scope="col">Inkoper</th><th scope="col">Uitbetaling</th><th scope="col">Termijn</th><th scope="col">Gratis retour bij een lager bod</th><th scope="col">Kapotte toestellen</th><th scope="col">Bron</th><th scope="col"><span style="position:absolute;left:-9999px">Link</span></th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <p class="empty" id="empty" hidden>Geen inkoper voldoet aan al je keuzes. Haal een vinkje weg om meer inkopers te zien.</p>
</section>
"""
    page("/", "Telefoon verkopen: inkopers vergeleken | GadgetDeal",
         "Vergelijk waar je je oude telefoon verkoopt: uitbetaling in geld of tegoed, termijn, gratis retour en kapotte toestellen.",
         body, '<script src="/assets/filter.js" defer></script>')


def sim_only() -> None:
    sim_gecontroleerd = nl_datum("2026-10-28")
    netwerken = [
        ("Op het netwerk van KPN", [
            ("KPN", "https://www.kpn.com"),
            ("Budget Thuis Mobiel", "https://www.budgetthuis.nl"),
            ("Lebara", "https://www.lebara.nl"),
            ("Simyo", "https://www.simyo.nl"),
            ("Youfone", "https://www.youfone.nl"),
        ]),
        ("Op het netwerk van Vodafone", [
            ("Vodafone", "https://www.vodafone.nl"),
            ("50+ Mobiel", "https://www.50plusmobiel.nl"),
            ("hollandsnieuwe", "https://www.hollandsnieuwe.nl"),
        ]),
        ("Op het netwerk van Odido", [
            ("Odido", "https://www.odido.nl"),
            ("Ben", "https://www.ben.nl"),
            ("Simpel", "https://www.simpel.nl"),
        ]),
        ("Netwerk nog niet door ons gecontroleerd", [
            ("Lycamobile", "https://www.lycamobile.nl"),
        ]),
    ]
    blokken = ""
    for titel, lijst in netwerken:
        items = "".join(
            f'<li><strong>{escape(n)}</strong><a href="{u}" rel="nofollow noopener" target="_blank">Bekijk sim only bij {escape(n)}</a></li>'
            for n, u in lijst
        )
        blokken += f"<h3>{titel}</h3><ul class=\"cards\">{items}</ul>"
    body = f"""
<article class="wrap prose">
  <h1>Telefoon verkocht? Kies ook een abonnement</h1>
  <p class="lead">Heb je je oude telefoon verkocht en een nieuwe los gekocht? Dan heb je alleen nog een simkaart met een abonnement nodig: sim only.</p>
  <h2>Waar je op let</h2>
  <ul>
    <li><strong>Data per maand.</strong> Kijk in je instellingen hoeveel je nu gemiddeld gebruikt, en kies niet veel meer. <a href="/uitleg/hoeveel-data-heb-ik-nodig/">Zo zie je je verbruik</a>.</li>
    <li><strong>Looptijd.</strong> Je kiest meestal tussen een vaste looptijd en maandelijks opzegbaar. Vergelijk de prijs van beide.</li>
    <li><strong>Netwerk.</strong> Er zijn in Nederland drie landelijke mobiele netwerken: KPN, Vodafone en Odido. Andere aanbieders gebruiken een van die drie. Hieronder zie je welke.</li>
    <li><strong>Overstappen.</strong> Je kunt je nummer meestal meenemen; dat regelt de nieuwe aanbieder. <a href="/uitleg/overstappen-naar-sim-only/">Zo werkt overstappen</a>.</li>
  </ul>
  <h2>Aanbieders per netwerk</h2>
  {blokken}
  <p class="source">Netwerken gecontroleerd op {sim_gecontroleerd} via <a href="https://simvergelijk.nl/mobiele-providers/" rel="nofollow noopener">Simvergelijk</a> en <a href="https://www.providers.nl/mobiel/budget-mobiel/" rel="nofollow noopener">Providers.nl</a>. Prijzen en acties veranderen vaak; check ze bij de aanbieder. Mist er een aanbieder? <a href="/contact/">Laat het weten</a>.</p>
</article>
"""
    page("/sim-only/", "Sim only kiezen na je nieuwe telefoon | GadgetDeal",
         "Waar je op let bij een sim-only-abonnement, met de aanbieders per netwerk op een rij.", body)


def uitleg() -> None:
    page("/uitleg/", "Uitleg over telefoon verkopen | GadgetDeal",
         "Praktische uitleg over je telefoon verkopen: resetten, geld of tegoed en een inkoper kiezen.", """
<article class="wrap prose">
  <h1>Uitleg</h1>
  <ul class="cards">
    <li><strong>Je iPhone klaarmaken voor verkoop</strong>Back-up, uitloggen en wissen, in de juiste volgorde.<br><a href="/uitleg/iphone-klaarmaken-voor-verkoop/">Lees de stappen</a></li>
    <li><strong>Geld of tegoed?</strong>Wanneer een cadeaubon slim is, en wanneer niet.<br><a href="/uitleg/geld-of-tegoed/">Lees meer</a></li>
    <li><strong>Een inkoper kiezen</strong>Wat er gebeurt als ze na controle minder bieden.<br><a href="/uitleg/inkoper-kiezen/">Lees meer</a></li>
    <li><strong>Overstappen naar sim only</strong>Je nummer meenemen en wanneer je kosteloos opzegt.<br><a href="/uitleg/overstappen-naar-sim-only/">Lees meer</a></li>
    <li><strong>Hoeveel data heb ik nodig?</strong>Zo zie je je eigen verbruik en kies je de juiste bundel.<br><a href="/uitleg/hoeveel-data-heb-ik-nodig/">Lees meer</a></li>
  </ul>
</article>
""")

    page("/uitleg/iphone-klaarmaken-voor-verkoop/", "iPhone klaarmaken voor verkoop | GadgetDeal",
         "Zo maak je je iPhone klaar voor verkoop: back-up maken, uitloggen bij je Apple-account en alles wissen.", """
<article class="wrap prose">
  <h1>Je iPhone klaarmaken voor verkoop</h1>
  <p class="lead">Een inkoper kan een iPhone die nog aan jouw Apple-account gekoppeld is niet doorverkopen. Doe deze stappen in deze volgorde.</p>
  <ol>
    <li><strong>Maak een back-up.</strong> Tik in Instellingen op je naam, dan op iCloud &gt; iCloud-back-up, en kies 'Maak nu back-up'. Of maak een back-up op je computer.</li>
    <li><strong>Log uit bij iCloud.</strong> Tik in Instellingen op je naam en kies 'Log uit'.</li>
    <li><strong>Wis je iPhone.</strong> Sluit hem aan op de lader. Ga naar Instellingen &gt; Algemeen &gt; 'Zet over of stel iPhone opnieuw in' en kies 'Wis alle content en instellingen'. Je hebt je toegangscode en het wachtwoord van je Apple-account nodig.</li>
    <li><strong>Haal je simkaart eruit.</strong> Gebruik je een eSIM die je niet meer nodig hebt, wis die dan ook.</li>
    <li><strong>Noteer je IMEI-nummer en maak foto's.</strong> Het IMEI-nummer zie je door *#06# in te toetsen. Foto's van de staat helpen als de inkoper na controle een lager bod doet.</li>
  </ol>
  <p class="note">De menunamen kunnen per iOS-versie iets verschillen. Zoek in Instellingen op 'wis' als je de optie niet ziet.</p>
  <p class="source">Bronnen: <a href="https://www.iculture.nl/tips/iphone-verkoopklaar-maken/" rel="nofollow noopener">iCulture, iPhone verkoopklaar maken</a>, <a href="https://www.verkopen.nl/veelgestelde-vragen" rel="nofollow noopener">Verkopen.nl, veelgestelde vragen</a> (volgorde: back-up, uitloggen, wissen, simkaart eruit) en de checklist in de <a href="https://nomophone.com/nl/guides/marche/waar-telefoon-verkopen-vergelijking" rel="nofollow noopener">NomoPhone-gids</a> (eSIM, IMEI, foto's). Gecontroleerd op 28 oktober 2026.</p>
</article>
""")

    geld = ", ".join(b["naam"] for b in sorted(DATA["inkopers"], key=lambda b: b["naam"].lower()) if b["geld"])
    tegoed = ", ".join(b["naam"] for b in sorted(DATA["inkopers"], key=lambda b: b["naam"].lower()) if not b["geld"])
    page("/uitleg/geld-of-tegoed/", "Telefoon verkopen: geld of tegoed? | GadgetDeal",
         "Een cadeaubon of korting is soms meer waard dan geld, maar bindt je aan één winkel. Zo kies je.", f"""
<article class="wrap prose">
  <h1>Geld of tegoed?</h1>
  <p class="lead">Sommige inkopers betalen je uit op je rekening. Andere geven een cadeaubon, tegoed of korting op een nieuw toestel.</p>
  <h2>Wanneer tegoed slim is</h2>
  <p>Als je toch al iets bij die winkel wilt kopen. Tegoed is soms meer waard: bij Rebuy is een waardebon 10% meer waard dan uitbetaling in geld.</p>
  <h2>Wanneer geld beter is</h2>
  <p>Als je je nieuwe telefoon ergens anders koopt, of nog niet weet wat je wilt. Tegoed kun je maar bij één winkel uitgeven, en een bon kan verlopen.</p>
  <h2>Wie betaalt wat</h2>
  <p><strong>Geld:</strong> {escape(geld)}.</p>
  <p><strong>Tegoed, cadeaubon of korting:</strong> {escape(tegoed)}.</p>
  <p class="source">Volgens de voorwaarden van de inkopers, gecontroleerd op {GECONTROLEERD}. <a href="/">Bekijk de vergelijking</a></p>
</article>
""")

    page("/uitleg/inkoper-kiezen/", "Een inkoper kiezen voor je telefoon | GadgetDeal",
         "Inkopers verlagen hun bod soms na controle. Let daarom op wat er gebeurt als je dat lagere bod weigert.", f"""
<article class="wrap prose">
  <h1>Een inkoper kiezen</h1>
  <p class="lead">Het bod dat je online krijgt, is nog niet definitief. De inkoper controleert je toestel eerst.</p>
  <h2>Het bod kan lager uitvallen</h2>
  <p>Wijkt de staat af van wat je hebt ingevuld, dan krijg je een nieuw, lager bod. Dat gebeurde in een praktijkproef van de Consumentenbond uit 2017 bij 7 van de 12 ingestuurde toestellen.</p>
  <h2>Let op wat er gebeurt als je nee zegt</h2>
  <p>Van de {len(DATA["inkopers"])} inkopers in onze vergelijking vermelden er {sum(1 for b in DATA["inkopers"] if b["retour"] == "ja")} dat ze je toestel dan gratis terugsturen. Bij KPN Trade-in betaal je de retourzending zelf, en bij de rest staat niet of het gratis is. Check dat vóór je opstuurt.</p>
  <h2>Zo voorkom je een tegenvaller</h2>
  <ul>
    <li>Vul de staat eerlijk in, ook kleine krassen.</li>
    <li>Maak foto's voordat je je telefoon inpakt.</li>
    <li>Vraag bij twee of drie inkopers een bod aan. Er is niet één inkoper die altijd het meest biedt.</li>
  </ul>
  <p class="source">Bronnen: <a href="https://www.telecompaper.com/nieuws/grote-prijsverschillen-inkoopsites-gebruikte-smartphones--1194782" rel="nofollow noopener">Telecompaper over de praktijkproef van de Consumentenbond (2017)</a>, <a href="https://www.consumentenbond.nl/smartphone/smartphone-verkopen-online" rel="nofollow noopener">Consumentenbond, telefoon verkopen</a> (niet één inkoper biedt altijd het meest), en de bronnen per inkoper in <a href="/">de vergelijking</a>.</p>
</article>
""")

    page("/uitleg/overstappen-naar-sim-only/", "Overstappen naar sim only met je eigen nummer | GadgetDeal",
         "Zo stap je over naar een sim-only-abonnement: je nummer meenemen, wanneer je kosteloos opzegt en wat de nieuwe aanbieder voor je regelt.", f"""
<article class="wrap prose">
  <h1>Overstappen naar sim only</h1>
  <p class="lead">Nieuwe telefoon gekocht en je oude verkocht? Dan heb je geen abonnement met toestel meer nodig. Met sim only betaal je alleen voor bellen en internet, en je kunt je eigen nummer houden.</p>
  <h2>Check eerst je huidige contract</h2>
  <p>Kijk in je account bij je huidige aanbieder tot wanneer je vaste looptijd loopt.</p>
  <ul>
    <li><strong>Is je vaste looptijd voorbij?</strong> Dan kun je kosteloos opzeggen. De opzegtermijn is dan maximaal een maand.</li>
    <li><strong>Loopt je contract nog?</strong> Dan kun je meestal wel opzeggen, maar vaak tegen kosten. Wat je betaalt, staat in je contract.</li>
  </ul>
  <h2>Je nummer meenemen</h2>
  <p>Dat heet nummerbehoud. Je regelt het bij je <strong>nieuwe</strong> aanbieder: bij het afsluiten geef je aan dat je je nummer wilt meenemen. De nieuwe en de oude aanbieder regelen de overstap dan onderling. Je oude abonnement wordt daarbij meestal ook opgezegd, dus je hoeft dat niet zelf te doen.</p>
  <p class="note">Volgens de ACM zegt je nieuwe aanbieder je oude abonnement voor je op. Vergeet hij dat, zeg dan zelf zo snel mogelijk op om dubbele kosten te voorkomen.</p>
  <h2>Zo stap je over</h2>
  <ol>
    <li>Bekijk hoeveel data je nodig hebt. <a href="/uitleg/hoeveel-data-heb-ik-nodig/">Zo zie je je verbruik</a>.</li>
    <li>Kies een aanbieder. <a href="/sim-only/">Bekijk de aanbieders per netwerk</a>.</li>
    <li>Sluit het abonnement af en kies voor nummerbehoud. Houd je huidige nummer en je klantnummer bij de oude aanbieder bij de hand.</li>
    <li>Wacht op je nieuwe simkaart of eSIM, en activeer hem op de datum die je nieuwe aanbieder doorgeeft.</li>
  </ol>
  <p class="source">Bronnen: <a href="https://www.acm.nl/nl/node/24843" rel="nofollow noopener">ACM, opzeggen of overstappen van uw telecomabonnement</a> en <a href="https://www.mobiel.nl/vragen-en-contact/providers/wat-is-belangrijk-om-te-weten-over-mijn-abonnement/opzeggen" rel="nofollow noopener">Mobiel.nl, opzeggen</a>. Gecontroleerd op 28 oktober 2026. De precieze voorwaarden verschillen per aanbieder.</p>
</article>
""")

    page("/uitleg/hoeveel-data-heb-ik-nodig/", "Hoeveel mobiele data heb ik nodig? | GadgetDeal",
         "Zo bekijk je op je iPhone of Android hoeveel mobiele data je gebruikt, en kies je een sim-only-bundel die past.", f"""
<article class="wrap prose">
  <h1>Hoeveel data heb ik nodig?</h1>
  <p class="lead">De beste maat ben je zelf. Kijk hoeveel je de afgelopen maanden echt hebt gebruikt, in plaats van te gokken.</p>
  <h2>Je verbruik bekijken op een iPhone</h2>
  <ol>
    <li>Ga naar <strong>Instellingen &gt; Mobiel netwerk</strong>.</li>
    <li>Scroll omlaag. Je ziet het totaal en per app hoeveel mobiele data die gebruikte.</li>
    <li>Let op: dit verbruik telt over een bepaalde periode; welke, staat onderaan de lijst. Onderaan kun je met <strong>Stel gegevens opnieuw in</strong> de teller op nul zetten. Doe dat aan het begin van je bundelmaand, dan zie je na een maand precies wat je gebruikt.</li>
  </ol>
  <h2>Je verbruik bekijken op Android</h2>
  <ol>
    <li>Ga naar <strong>Instellingen &gt; Netwerk en internet &gt; Simkaarten</strong>.</li>
    <li>Tik op <strong>Datagebruik van app</strong> voor het verbruik per app.</li>
  </ol>
  <p>De namen van menu's verschillen per merk en Android-versie. Vind je ze niet, zoek dan in Instellingen naar 'datagebruik'.</p>
  <h2>Ook je huidige aanbieder weet het</h2>
  <p>In de app of het online account van je aanbieder zie je meestal je verbruik per maand. Kijk naar een paar maanden, want het verschilt per maand, bijvoorbeeld als je op vakantie bent geweest.</p>
  <h2>Een bundel kiezen</h2>
  <ul>
    <li>Neem je hoogste verbruik van de afgelopen maanden, met een kleine marge erbovenop.</li>
    <li>Kom je soms net tekort? Vergelijk dan wat een iets grotere bundel kost met wat extra data bijkopen je per keer kost.</li>
    <li>Gebruik je veel wifi, thuis en op werk of school, dan heb je vaak minder mobiele data nodig dan je denkt.</li>
  </ul>
  <p><a href="/sim-only/">Bekijk de sim-only-aanbieders per netwerk</a></p>
  <p class="source">Bronnen voor de menupaden: <a href="https://www.iculture.nl/tips/dataverbruik-apps-iphone/" rel="nofollow noopener">iCulture (iPhone)</a> en <a href="https://www.androidplanet.nl/tips/dataverbruik-controleren-op-android/" rel="nofollow noopener">Android Planet (Android)</a>. Gecontroleerd op 28 oktober 2026.</p>
</article>
""")


def static_pages() -> None:
    page("/hoe-wij-vergelijken/", "Hoe wij vergelijken | GadgetDeal",
         "Hoe GadgetDeal inkopers vergelijkt, waar de gegevens vandaan komen en hoe wij geld verdienen.", f"""
<article class="wrap prose">
  <h1>Hoe wij vergelijken</h1>
  <h2>Wat we vergelijken</h2>
  <p>Per inkoper: hoe je wordt uitbetaald, hoe snel, of je je toestel gratis terugkrijgt als je een lager bod weigert, en of ze kapotte toestellen kopen.</p>
  <h2>Welke inkopers we opnemen</h2>
  <p>Inkopers en inruilprogramma's waar je in Nederland als particulier je telefoon kunt verkopen, en waarvan we de voorwaarden online konden vinden. De lijst is niet volledig. Mist er een? <a href="/contact/">Laat het weten</a>.</p>
  <p>Twee inkopers, Leapp en Verkopen.nl, gebruiken hetzelfde inkoopplatform (Trade in). Hun voorwaarden zijn gelijk en hun biedingen waarschijnlijk ook.</p>
  <h2>Waar de gegevens vandaan komen</h2>
  <p>Uit de eigen pagina's en voorwaarden van de inkopers. Een deel van de officiële pagina's konden we niet zelf openen; die gegevens hebben we gecontroleerd via de <a href="https://nomophone.com/nl/guides/marche/waar-telefoon-verkopen-vergelijking" rel="nofollow noopener">vergelijkingsgids van NomoPhone</a>, die per feit de officiële pagina citeert. Dat staat bij die inkopers vermeld. Let op: NomoPhone is zelf ook inkoper.</p>
  <p>Staat iets nergens vermeld, dan zetten we 'Niet vermeld' neer; we vullen niets zelf in. Bij elke inkoper linken we naar de bron. Laatste controle: {GECONTROLEERD}.</p>
  <h2>Volgorde</h2>
  <p>Inkopers staan op alfabet, gegroepeerd op geld of tegoed. Een inkoper staat niet hoger omdat wij er iets aan verdienen.</p>
  <h2>Hoe wij geld verdienen</h2>
  <p>Bij sommige links kunnen we een vergoeding ontvangen als je via ons iets verkoopt of afsluit. Bij welke links dat zo is, staat onder de knop. Jij betaalt daar niets extra voor.</p>
  <h2>Fout gezien?</h2>
  <p>Laat het weten via de <a href="/contact/">contactpagina</a>. We passen het zo snel mogelijk aan.</p>
</article>
""")

    page("/privacy/", "Privacy | GadgetDeal", "Privacyverklaring van GadgetDeal.", """
<article class="wrap prose">
  <h1>Privacy</h1>
  <p class="source">Laatst bijgewerkt op 28 oktober 2026.</p>
  <h2>Wie we zijn</h2>
  <p>GadgetDeal (gadgetdeal.nl) wordt beheerd door Joris Krom. Contact: info@gadgetdeal.nl.</p>
  <h2>Welke gegevens we verwerken</h2>
  <ul>
    <li><strong>Bezoek aan de site.</strong> We gebruiken geen tracking, geen analytics en geen advertentiecookies. De site wordt gehost door Vercel. Om de site te kunnen tonen, verwerkt Vercel technische gegevens zoals je IP-adres.</li>
    <li><strong>Lettertype.</strong> Het lettertype wordt geladen via Google Fonts. Daarbij ziet Google je IP-adres.</li>
    <li><strong>Als je ons mailt.</strong> We gebruiken je naam, mailadres en bericht alleen om je te antwoorden. We bewaren je mail niet langer dan nodig om je vraag af te handelen.</li>
  </ul>
  <h2>Cookies</h2>
  <p>Deze site plaatst zelf geen cookies. Klik je via een link door naar een inkoper of aanbieder, dan kan die partij of het affiliatenetwerk daar cookies plaatsen om bij te houden dat je via GadgetDeal kwam. Daarvoor geldt hun eigen cookie- en privacybeleid.</p>
  <h2>Je rechten</h2>
  <p>Je kunt ons vragen welke gegevens we van je hebben, en vragen om die te corrigeren of te verwijderen. Mail daarvoor naar info@gadgetdeal.nl. Ben je het niet eens met hoe we met je gegevens omgaan, dan kun je een klacht indienen bij de <a href="https://autoriteitpersoonsgegevens.nl" rel="nofollow noopener">Autoriteit Persoonsgegevens</a>.</p>
  <h2>Links naar andere sites</h2>
  <p>Klik je door naar een inkoper of aanbieder, dan geldt hun privacybeleid.</p>
</article>
""")

    page("/contact/", "Contact | GadgetDeal", "Neem contact op met GadgetDeal.", """
<article class="wrap prose">
  <h1>Contact</h1>
  <p class="lead">Een fout gezien, een inkoper die ontbreekt of een vraag over samenwerking? Mail naar <a href="mailto:info@gadgetdeal.nl">info@gadgetdeal.nl</a>.</p>
  <p>Let op: wij kopen zelf geen telefoons in. Voor vragen over een verkoop neem je contact op met de inkoper.</p>
</article>
""")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    home()
    sim_only()
    uitleg()
    static_pages()
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    urls = sorted(p.parent.relative_to(OUT).as_posix() for p in OUT.rglob("index.html"))
    entries = "".join(
        f"<url><loc>{SITE}/{'' if u == '.' else u + '/'}</loc><lastmod>{LAATST_BIJGEWERKT}</lastmod></url>"
        for u in urls
    )
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{entries}</urlset>',
        encoding="utf-8")
    print(f"Site gebouwd in {OUT} ({len(urls)} pagina's)")


if __name__ == "__main__":
    main()
