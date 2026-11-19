WILMA BUCHLY - LOKAAL ONTWERPVOORSTEL
19 november 2026

Preview: http://127.0.0.1:4173/
Uitvoer: dist/
Bron voor layout en inhoudsverwerking: build.py
Stijlen en interacties: src/styles.css en src/app.js

Deze versie is een ontwerpvoorstel. GitHub-repository: https://github.com/makemywebsiteio-ai/WilmaBuchly2
Hostingdeployment en wijzigingen aan het oorspronkelijke domein vallen niet onder deze GitHub-overdracht.

WERKWIJZE
Lees de door de opdrachtgever aangeleverde Masterprompt-Websiteverfijning.txt opnieuw vóór iedere grote aanpassingsronde. De originele prompt is leidend voor behoud van inhoud, identiteit, bronmateriaal, previewstatus en controle. Maak wijzigingen in build.py of src/, niet uitsluitend in dist/.

Bouwen:
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
  .venv/bin/python build.py
  .venv/bin/python check.py
  node --check src/app.js

Lokaal bekijken:
  python3 -m http.server 4173 --bind 127.0.0.1 --directory dist

Maak de buildomgeving lokaal aan met bovenstaande commando's.

BRONMATERIAAL
research/routes.json koppelt de 73 opgehaalde pagina's aan hun oorspronkelijke URL.
research/assets.json bewaart de herkomst van afbeeldingen.
research/responsive-images.json beschrijft de scherpe, proportioneel verkleinde beeldvarianten.
research/animation-review.txt documenteert de onderzochte FreeFrontend-voorbeelden, werkelijk gelezen code, beperkingen en toegepaste principes.
research/animation-cards.json inventariseert 33 referentiekaarten.
De bron-HTML blijft in research/ bewaard voor inhoudsvergelijking. Scripts en tracking uit deze archieven worden niet uitgevoerd door de preview.

PREVIEWGEDRAG
- De oorspronkelijke logo's, foto's, teksten, contactgegevens, pagina-inhoud en bereikbare downloads zijn de basis.
- De zes blogartikelen en gevonden productpagina's hebben lokale routes.
- Categorieën, zoeken en sorteren werken lokaal. Bestellen, betalen en accountbeheer blijven op de oorspronkelijke website.
- Het contactformulier is een lokale veldgroep zonder form-element, named inputs, netwerkendpoint of gegevensopslag. Alleen e-mail is verplicht; het bericht heeft de oorspronkelijke limiet van 180 tekens. Enter start uitsluitend lokale validatie. Zonder JavaScript kan niets worden verzonden.
- Vimeo wordt uitsluitend na een bewuste klik geladen. Het oorspronkelijke openbare audiofragment is lokaal aanwezig.
- Alleen de keuze om animaties te pauzeren wordt opgeslagen. Verminderde beweging wordt automatisch gerespecteerd. Achtergrondbeweging pauzeert buiten beeld en in verborgen tabbladen.
- De bronwebsite bevat gezondheids- en productclaims. Die zijn als broninhoud behouden, niet onafhankelijk bevestigd of uitgebreid.
- Bronprijzen, voorraad, reviews, kwalificaties en licenties zijn een momentopname en moeten vóór productie door de eigenaar worden bevestigd.

ANIMATIES
Eigen kleine implementatie zonder GSAP/Three.js-dependency of gekopieerde demo-assets. Native Web Animations API voor gespreide inkomst, consistente cubic-bezier easing, onderbreekbare uitklap- en menuovergangen, foto-lightbox en FLIP bij productsortering. Herhaalde bladcontouren en gradientvormen delen één silhouette. Geen scroll-hijacking; inhoud blijft zonder JavaScript beschikbaar.

RECHTEN
Onofficieel ontwerpvoorstel door MakeMyWebsite. Teksten, logo en oorspronkelijke beelden behoren aan Wilma Buchly en betrokken rechthebbenden. Openbare beschikbaarheid is geen gebruikslicentie. De preview bevat noindex en een zichtbare statusmelding.
