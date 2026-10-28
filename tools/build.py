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
    return f"""<tr data-naam="{escape(b['naam'])}" data-group="{group}" data-geld="{str(b['geld']).lower()}" data-retour="{b['retour']}" data-kapot="{b['kapot']}">
  <th scope="row">{escape(b['naam'])}{note}</th>
  <td data-label="Uitbetaling">{escape(b['uitbetaling'])}</td>
  <td data-label="Termijn">{escape(b['termijn'])}</td>
  <td data-label="Gratis retour bij een lager bod">{mark(b['retour'])}</td>
  <td data-label="Kapotte toestellen">{mark(b['kapot'])}</td>
  <td data-label="Bron"><a class="source" href="{escape(b['bron'])}" rel="nofollow noopener">Voorwaarden</a></td>
  <td class="cta"><a class="go" href="{escape(link)}" rel="{rel}" target="_blank" aria-label="Bod opvragen bij {escape(b['naam'])}">Bod opvragen</a>{paid}</td>
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
    <p>Hier zie je het naast elkaar, uit de voorwaarden van {total} inkopers.</p>
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
  <p>Op alfabet, niet op hoe veel wij eraan verdienen. Prijzen tonen we nog niet: die hangen af van je model, opslag en de staat van je toestel. Vraag bij twee of drie inkopers een bod aan. Gecontroleerd op {GECONTROLEERD}.</p>
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
  <p class="lead">Wie een nieuwe telefoon koopt, kan vaak ook besparen op zijn abonnement. Met een losse telefoon heb je alleen een simkaart nodig.</p>
  <h2>Waar je op let</h2>
  <ul>
    <li><strong>Data per maand.</strong> Kijk in je instellingen hoeveel je nu gemiddeld gebruikt, en kies niet veel meer.</li>
    <li><strong>Looptijd.</strong> Een maandelijks opzegbaar abonnement is soms iets duurder, maar je zit nergens aan vast.</li>
    <li><strong>Netwerk.</strong> Er zijn in Nederland drie mobiele netwerken: KPN, Vodafone en Odido. De meeste andere aanbieders gebruiken een van die drie. Aanbieders op hetzelfde netwerk hebben hetzelfde bereik.</li>
    <li><strong>Overstappen.</strong> Je kunt je nummer meestal meenemen; dat regelt de nieuwe aanbieder.</li>
  </ul>
  <h2>Aanbieders per netwerk</h2>
  {blokken}
  <p class="source">Netwerken gecontroleerd op {sim_gecontroleerd} via <a href="https://simvergelijk.nl/mobiele-providers/" rel="nofollow noopener">Simvergelijk</a> en <a href="https://www.providers.nl/mobiel/budget-mobiel/" rel="nofollow noopener">Providers.nl</a>. Prijzen en acties veranderen vaak; check ze bij de aanbieder. Mist er een aanbieder? <a href="/contact/">Laat het weten</a>.</p>
</article>
"""
    page("/sim-only/", "Sim only kiezen na je nieuwe telefoon | GadgetDeal",
         "Waar je op let bij een sim-only-abonnement, met alle aanbieders per netwerk op een rij.", body)


def uitleg() -> None:
    page("/uitleg/", "Uitleg over telefoon verkopen | GadgetDeal",
         "Praktische uitleg over je telefoon verkopen: resetten, geld of tegoed en een inkoper kiezen.", """
<article class="wrap prose">
  <h1>Uitleg</h1>
  <ul class="cards">
    <li><strong>Je iPhone klaarmaken voor verkoop</strong>Back-up, uitloggen en wissen, in de juiste volgorde.<br><a href="/uitleg/iphone-klaarmaken-voor-verkoop/">Lees de stappen</a></li>
    <li><strong>Geld of tegoed?</strong>Wanneer een cadeaubon slim is, en wanneer niet.<br><a href="/uitleg/geld-of-tegoed/">Lees meer</a></li>
    <li><strong>Een inkoper kiezen</strong>Wat er gebeurt als ze na controle minder bieden.<br><a href="/uitleg/inkoper-kiezen/">Lees meer</a></li>
  </ul>
</article>
""")

    page("/uitleg/iphone-klaarmaken-voor-verkoop/", "iPhone klaarmaken voor verkoop | GadgetDeal",
         "Zo maak je je iPhone klaar voor verkoop: back-up maken, uitloggen bij je Apple-account en alles wissen.", """
<article class="wrap prose">
  <h1>Je iPhone klaarmaken voor verkoop</h1>
  <p class="lead">Een inkoper kan een iPhone die nog aan jouw Apple-account hangt niet doorverkopen. Doe deze stappen in deze volgorde.</p>
  <ol>
    <li><strong>Maak een back-up.</strong> Via iCloud of op je computer, zodat je je foto's, berichten en apps op je nieuwe telefoon terugzet.</li>
    <li><strong>Ontkoppel je Apple Watch</strong>, als je die hebt, via de Watch-app.</li>
    <li><strong>Log uit bij je Apple-account.</strong> Ga naar Instellingen, tik op je naam en kies 'Log uit'. Daarmee zet je ook 'Zoek mijn' uit.</li>
    <li><strong>Wis je iPhone.</strong> Ga naar Instellingen &gt; Algemeen &gt; 'Zet over of stel iPhone opnieuw in' &gt; 'Wis alle inhoud en instellingen'.</li>
    <li><strong>Haal je simkaart eruit.</strong> Gebruik je een eSIM, vraag dan je provider hoe je die overzet naar je nieuwe telefoon.</li>
    <li><strong>Noteer je IMEI-nummer en maak foto's.</strong> Het IMEI-nummer zie je door *#06# te bellen. Foto's van de staat helpen als de inkoper na controle een lager bod doet.</li>
  </ol>
  <p class="note">Doe stap 3 vóór stap 4. Wis je eerst, dan kan 'Zoek mijn' de telefoon blijven vergrendelen.</p>
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
  <p>Wijkt de staat af van wat je hebt ingevuld, dan krijg je een nieuw, lager bod. Dat gebeurt geregeld: in een praktijkproef van de Consumentenbond (2017) verlaagden inkopers hun bod bij 7 van de 12 ingestuurde toestellen.</p>
  <h2>Let op wat er gebeurt als je nee zegt</h2>
  <p>De meeste inkopers in onze vergelijking sturen je toestel dan gratis terug. Niet allemaal: bij KPN Trade-in betaal je de retourzending zelf. En sommige inkopers vermelden het niet. Check dat vóór je opstuurt.</p>
  <h2>Zo voorkom je een tegenvaller</h2>
  <ul>
    <li>Vul de staat eerlijk in, ook kleine krassen.</li>
    <li>Maak foto's voordat je je telefoon inpakt.</li>
    <li>Vraag bij twee of drie inkopers een bod aan. Er is niet één inkoper die altijd het meest biedt.</li>
  </ul>
  <p class="source">Bronnen: <a href="https://www.consumentenbond.nl/nieuws/2017/grote-verschillen-tussen-inkoopsites-voor-smartphones" rel="nofollow noopener">Consumentenbond (2017)</a>, <a href="https://www.consumentenbond.nl/smartphone/smartphone-verkopen-online" rel="nofollow noopener">Consumentenbond, telefoon verkopen</a>, en de voorwaarden van de inkopers (gecontroleerd op {GECONTROLEERD}).</p>
</article>
""")


def static_pages() -> None:
    page("/hoe-wij-vergelijken/", "Hoe wij vergelijken | GadgetDeal",
         "Hoe GadgetDeal inkopers vergelijkt, waar de gegevens vandaan komen en hoe wij geld verdienen.", f"""
<article class="wrap prose">
  <h1>Hoe wij vergelijken</h1>
  <h2>Wat we vergelijken</h2>
  <p>Per inkoper: hoe je wordt uitbetaald, hoe snel, of je je toestel gratis terugkrijgt als je een lager bod weigert, en of ze kapotte toestellen kopen.</p>
  <h2>Waar de gegevens vandaan komen</h2>
  <p>Uit de eigen pagina's en voorwaarden van elke inkoper. Staat iets er niet, dan zetten we 'Niet vermeld' neer; we vullen niets zelf in. Bij elke inkoper linken we naar de bron. Laatste controle: {GECONTROLEERD}.</p>
  <h2>Volgorde</h2>
  <p>Inkopers staan op alfabet, gegroepeerd op geld of tegoed. Een inkoper staat niet hoger omdat wij er iets aan verdienen.</p>
  <h2>Hoe wij geld verdienen</h2>
  <p>Bij sommige links ontvangen we een vergoeding als je via ons iets verkoopt of afsluit. Dat staat dan onder de knop. Jij betaalt daar niets extra voor.</p>
  <h2>Fout gezien?</h2>
  <p>Laat het weten via de <a href="/contact/">contactpagina</a>. We passen het zo snel mogelijk aan.</p>
</article>
""")

    page("/privacy/", "Privacy | GadgetDeal", "Privacyverklaring van GadgetDeal.", """
<article class="wrap prose">
  <h1>Privacy</h1>
  <h2>Wie we zijn</h2>
  <p>GadgetDeal (gadgetdeal.nl) wordt beheerd door Joris Krom. Contact: info@gadgetdeal.nl.</p>
  <h2>Welke gegevens we verzamelen</h2>
  <p>Op dit moment geen. We gebruiken geen tracking, geen analytics en geen advertentiecookies. Het lettertype wordt geladen via Google Fonts; daarbij ziet Google je IP-adres.</p>
  <h2>Cookies</h2>
  <p>Deze site plaatst zelf geen cookies. Klik je via een link door naar een inkoper of aanbieder, dan kan die partij of het affiliatenetwerk daar cookies plaatsen om bij te houden dat je via GadgetDeal kwam. Daarvoor geldt hun eigen cookie- en privacybeleid.</p>
  <h2>Links naar andere sites</h2>
  <p>Klik je door naar een inkoper of aanbieder, dan geldt hun privacybeleid.</p>
  <h2>Contact</h2>
  <p>Vragen over privacy? Mail naar info@gadgetdeal.nl.</p>
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
    (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://gadgetdeal.nl/sitemap.xml\n", encoding="utf-8")
    urls = sorted(p.parent.relative_to(OUT).as_posix() for p in OUT.rglob("index.html"))
    entries = "".join(
        f"<url><loc>https://gadgetdeal.nl/{'' if u == '.' else u + '/'}</loc><lastmod>{DATA['gecontroleerd']}</lastmod></url>"
        for u in urls
    )
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{entries}</urlset>',
        encoding="utf-8")
    print(f"Site gebouwd in {OUT} ({len(urls)} pagina's)")


if __name__ == "__main__":
    main()
