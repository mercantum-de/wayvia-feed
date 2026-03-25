# Wayvia Feed — Sharp Consumer Electronics Deutschland

Automatischer Produktfeed fuer Wayvia (ehemals PriceSpider / Hatch).

## Was es tut

- Taeglich um ~14:00 Uhr holt ein GitHub Actions Workflow die aktuellen
  Produktdaten von `shop.sharpconsumer.de/products.json`
- Mergt die EAN-Codes aus `ean_mapping.json` dazu
- Erzeugt `feed/wayvia_feed_sharp.csv` im Wayvia-Format
- Committed die aktualisierte CSV automatisch

## Feed-URL fuer Wayvia

Nach dem Setup ist der Feed unter dieser festen URL erreichbar:

```
https://raw.githubusercontent.com/{DEIN_USER}/wayvia-feed/main/feed/wayvia_feed_sharp.csv
```

Diese URL an Wayvia weitergeben — fertig.

## Einrichtung (einmalig)

### 1. GitHub Repo erstellen

```powershell
cd C:\Claude-Code\Privat
git clone [dieses repo] wayvia-feed
cd wayvia-feed
git remote set-url origin https://github.com/{DEIN_USER}/wayvia-feed.git
git push -u origin main
```

Oder: Neues Repo auf GitHub erstellen, dann den Inhalt dieses Ordners pushen.

### 2. GitHub Actions erlauben

- Repo Settings → Actions → General
- "Allow all actions" aktivieren
- Unter "Workflow permissions": **Read and write permissions** aktivieren

### 3. Ersten Build manuell ausloesen

- Im Repo: Tab "Actions" → "Wayvia Feed Update" → "Run workflow"
- Pruefen ob die CSV korrekt gebaut wird

### 4. Feed-URL an Wayvia schicken

Die Raw-URL der CSV an Wayvia weitergeben. Fertig.

## Neues Produkt hinzugefuegt?

Wenn ein neues Produkt in Shopify angelegt wird:

1. EAN in `ean_mapping.json` nachtragen:
   ```json
   "NEUE-SKU": "1234567890123"
   ```
2. Committen und pushen
3. Beim naechsten Lauf wird das Produkt automatisch mit EAN im Feed sein

Das Script warnt in der GitHub Actions Log-Ausgabe wenn Produkte
ohne EAN-Mapping gefunden werden.

## Dateien

```
wayvia-feed/
├── build_feed.py              ← Hauptscript
├── ean_mapping.json           ← SKU → EAN Zuordnung
├── feed/
│   └── wayvia_feed_sharp.csv  ← Aktueller Feed (wird taeglich aktualisiert)
├── .github/
│   └── workflows/
│       └── feed.yml           ← GitHub Actions Workflow (taeglich 14:00)
└── README.md
```
