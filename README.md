# GadgetDeal

Vergelijkingssite voor wie zijn oude telefoon wil verkopen: welke inkoper betaalt in geld, hoe snel, en wat er gebeurt als je een lager bod weigert.

## Structuur

- `data/inkopers.json`: alle inkopers en hun voorwaarden. Hier pas je gegevens aan.
- `assets/`: CSS en het filterscript.
- `tools/build.py`: bouwt de site in `site/` (alleen standaard-Python nodig, geen pakketten).
- `site/`: de gebouwde site. Deze map zet Vercel online.

## Aanpassen

1. Wijzig `data/inkopers.json` (en zet `gecontroleerd` op de datum van je controle).
2. Draai `python3 tools/build.py`.
3. Commit en push; Vercel zet de nieuwe versie automatisch live.

Lokaal bekijken: `python3 -m http.server --directory site 8000` en open http://localhost:8000.

## Affiliate-links

Krijg je een affiliate-link van een inkoper, zet die dan in `affiliate_url` bij die inkoper. De knop gebruikt dan die link, krijgt `rel="sponsored"` en toont "Wij ontvangen commissie via deze link".

## Vóór publicatie

- Vul je naam in op de privacypagina (`static_pages` in `tools/build.py`).
- Maak het mailadres info@gadgetdeal.nl aan.
- Werk de privacypagina bij zodra je analytics, AdSense of cookies toevoegt.
