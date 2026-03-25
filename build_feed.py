"""
Wayvia Feed Builder fuer Sharp Consumer Electronics Deutschland
===============================================================
Holt die aktuelle Produktliste von Shopify (products.json),
mergt EAN-Codes aus der lokalen Mapping-Datei und erzeugt eine
Wayvia-kompatible CSV-Datei.

Wird taeglich um 14:00 per GitHub Actions ausgefuehrt.
"""

import json
import csv
import urllib.request
import os
import sys
from datetime import datetime, timezone

SHOP_URL = "https://shop.sharpconsumer.de/products.json?limit=250"
EAN_MAPPING_FILE = os.path.join(os.path.dirname(__file__), "ean_mapping.json")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "feed", "wayvia_feed_sharp.csv")
BRAND = "Sharp"


def fetch_products():
    """Holt alle Produkte aus dem oeffentlichen Shopify JSON-Feed."""
    all_products = []
    page = 1

    while True:
        url = f"{SHOP_URL}&page={page}"
        print(f"  Lade Seite {page}: {url}")

        req = urllib.request.Request(url, headers={"User-Agent": "WayviaFeedBot/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        products = data.get("products", [])
        if not products:
            break

        all_products.extend(products)
        page += 1

        # Sicherheit: max 10 Seiten (2500 Produkte)
        if page > 10:
            break

    return all_products


def load_ean_mapping():
    """Laedt das SKU → EAN Mapping."""
    with open(EAN_MAPPING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def build_feed(products, ean_map):
    """Baut die Wayvia CSV-Zeilen aus Shopify-Produkten + EAN-Mapping."""
    rows = []
    missing_eans = []

    for product in products:
        handle = product.get("handle", "")
        title = product.get("title", "")
        vendor = product.get("vendor", "")
        product_type = product.get("product_type", "Electronics")
        url = f"https://shop.sharpconsumer.de/products/{handle}"

        for variant in product.get("variants", []):
            sku = variant.get("sku", "").strip()
            if not sku:
                continue

            price = variant.get("price", "0.00")
            available = variant.get("available", False)
            stock = "1" if available else "0"

            # EAN aus Mapping holen
            ean = ean_map.get(sku, "")
            if not ean:
                missing_eans.append(sku)

            rows.append({
                "brand": BRAND,
                "ean": ean,
                "mpn": sku,
                "sku": sku,
                "product_name": title,
                "price": price,
                "url": url,
                "stock": stock,
                "category": product_type if product_type else "Electronics",
            })

    return rows, missing_eans


def write_csv(rows, filepath):
    """Schreibt die Wayvia CSV-Datei."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    fieldnames = ["brand", "ean", "mpn", "sku", "product_name", "price", "url", "stock", "category"]
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"=== Wayvia Feed Build — {now} ===\n")

    # 1. Produkte von Shopify holen
    print("1. Shopify-Produkte laden...")
    try:
        products = fetch_products()
        print(f"   → {len(products)} Produkte geladen\n")
    except Exception as e:
        print(f"   FEHLER beim Laden: {e}")
        sys.exit(1)

    # 2. EAN-Mapping laden
    print("2. EAN-Mapping laden...")
    ean_map = load_ean_mapping()
    print(f"   → {len(ean_map)} EAN-Eintraege\n")

    # 3. Feed bauen
    print("3. Feed bauen...")
    rows, missing_eans = build_feed(products, ean_map)
    print(f"   → {len(rows)} Produkt-Zeilen erstellt")

    if missing_eans:
        print(f"\n   ⚠ {len(missing_eans)} Produkte OHNE EAN:")
        for sku in missing_eans:
            print(f"     - {sku}")
        print("   → EAN in ean_mapping.json nachtragen!\n")

    # 4. CSV schreiben
    print(f"4. CSV schreiben: {OUTPUT_FILE}")
    write_csv(rows, OUTPUT_FILE)

    # 5. Zusammenfassung
    with_ean = len(rows) - len(missing_eans)
    print(f"\n=== FERTIG ===")
    print(f"Produkte gesamt: {len(rows)}")
    print(f"Mit EAN:         {with_ean}")
    print(f"Ohne EAN:        {len(missing_eans)}")
    print(f"Datei:           {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
