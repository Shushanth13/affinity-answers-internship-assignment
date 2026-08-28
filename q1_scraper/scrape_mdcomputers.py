import argparse
import csv
import json
import re
import sys
import time
import urllib.parse
from dataclasses import dataclass, asdict
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://mdcomputers.in/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
REQUEST_TIMEOUT = 15


@dataclass
class Product:
    name: str
    url: Optional[str]
    price: Optional[str]
    old_price: Optional[str]
    discount_pct: Optional[str]


def build_search_url(term: str, page: int = 1) -> str:
    params = {"route": "product/search", "search": term}
    if page > 1:
        params["page"] = str(page)
    return f"{BASE_URL}?{urllib.parse.urlencode(params)}"


def fetch_page(url: str, session: requests.Session) -> str:
    resp = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.text


PRICE_RE = re.compile(r"₹\s?[\d,]+")


def parse_products(html: str) -> List[Product]:
    soup = BeautifulSoup(html, "html.parser")
    products: List[Product] = []
    seen_urls = set()

    containers = soup.select(".product-thumb, .product-layout, .product-item")
    for c in containers:
        link = None
        for candidate in c.select("h4 a, .caption a, a[href*='/product/']"):
            if candidate.get_text(strip=True):
                link = candidate
                break
        if not link:
            continue
        name = link.get_text(strip=True)
        url = link.get("href")
        if not name or not url or url in seen_urls:
            continue

        price_new = c.select_one(".price-new, .price")
        price_old = c.select_one(".price-old")
        price_text = price_new.get_text(" ", strip=True) if price_new else ""
        prices_found = PRICE_RE.findall(price_text) or PRICE_RE.findall(
            c.get_text(" ", strip=True)
        )
        current_price = prices_found[-1] if prices_found else None
        old_price = (
            price_old.get_text(strip=True)
            if price_old
            else (prices_found[0] if len(prices_found) > 1 else None)
        )

        discount = None
        discount_match = re.search(r"-(\d+)%", c.get_text(" ", strip=True))
        if discount_match:
            discount = f"{discount_match.group(1)}%"

        products.append(
            Product(
                name=name,
                url=url,
                price=current_price,
                old_price=old_price if old_price != current_price else None,
                discount_pct=discount,
            )
        )
        seen_urls.add(url)

    NOISE_TEXT_RE = re.compile(
        r"^(-?\d+%|add to (cart|wishlist)|quick view|compare|₹[\d,]+)$", re.I
    )
    if not products:
        anchors_by_url = {}
        for link in soup.find_all("a", href=re.compile(r"/product/[\w\-]+")):
            url = link.get("href")
            if not url:
                continue
            anchors_by_url.setdefault(url, []).append(link)

        for url, links in anchors_by_url.items():
            if url in seen_urls:
                continue

            candidates = [
                (l.get_text(strip=True), l) for l in links
                if l.get_text(strip=True)
                and not NOISE_TEXT_RE.match(l.get_text(strip=True))
            ]
            if not candidates:
                continue
            name, best_link = max(candidates, key=lambda t: len(t[0]))

            ancestors = [set(id(a) for a in l.parents) for l in links]
            common_ancestor_ids = set.intersection(*ancestors) if ancestors else set()
            context_node = best_link
            for anc in best_link.parents:
                if id(anc) in common_ancestor_ids:
                    context_node = anc
                    break
            context_text = context_node.get_text(" ", strip=True)

            prices_found = PRICE_RE.findall(context_text)
            current_price = prices_found[-1] if prices_found else None
            old_price = prices_found[0] if len(prices_found) > 1 else None

            discount = None
            discount_match = re.search(r"-(\d+)%", context_text)
            if discount_match:
                discount = f"{discount_match.group(1)}%"

            products.append(
                Product(
                    name=name,
                    url=url,
                    price=current_price,
                    old_price=old_price if old_price != current_price else None,
                    discount_pct=discount,
                )
            )
            seen_urls.add(url)

    return products


def has_next_page(html: str) -> bool:
    soup = BeautifulSoup(html, "html.parser")
    return soup.find("a", string=re.compile(r"^>$|next", re.I)) is not None


def scrape(term: str, max_pages: int = 1, delay: float = 1.0) -> List[Product]:
    session = requests.Session()
    all_products: List[Product] = []

    for page in range(1, max_pages + 1):
        url = build_search_url(term, page)
        html = fetch_page(url, session)
        page_products = parse_products(html)
        if not page_products:
            break
        all_products.extend(page_products)

        if page < max_pages and has_next_page(html):
            time.sleep(delay)
        else:
            break

    return all_products


def output_results(products: List[Product], fmt: str, outfile: Optional[str]):
    if fmt == "json":
        data = json.dumps([asdict(p) for p in products], indent=2, ensure_ascii=False)
        if outfile:
            with open(outfile, "w", encoding="utf-8") as f:
                f.write(data)
        else:
            print(data)

    elif fmt == "csv":
        fh = open(outfile, "w", newline="", encoding="utf-8") if outfile else sys.stdout
        writer = csv.DictWriter(fh, fieldnames=["name", "url", "price", "old_price", "discount_pct"])
        writer.writeheader()
        for p in products:
            writer.writerow(asdict(p))
        if outfile:
            fh.close()

    else:
        if not products:
            print("No products found.")
            return
        for i, p in enumerate(products, 1):
            print(f"{i}. {p.name}")
            print(f"   Price: {p.price or 'N/A'}"
                  + (f" (was {p.old_price})" if p.old_price else "")
                  + (f" [{p.discount_pct} off]" if p.discount_pct else ""))
            print(f"   URL:   {p.url}")


def main():
    parser = argparse.ArgumentParser(description="Scrape product listings from mdcomputers.in")
    parser.add_argument("search_term", help="Product search term, e.g. 'external hard drive'")
    parser.add_argument("--pages", type=int, default=1, help="Max number of result pages to fetch (default: 1)")
    parser.add_argument("--format", choices=["table", "csv", "json"], default="table", help="Output format")
    parser.add_argument("-o", "--output", help="Write output to this file instead of stdout")
    args = parser.parse_args()

    try:
        products = scrape(args.search_term, max_pages=args.pages)
    except requests.RequestException as e:
        print(f"Error fetching data from mdcomputers.in: {e}", file=sys.stderr)
        sys.exit(1)

    output_results(products, args.format, args.output)
    print(f"\n{len(products)} product(s) found for '{args.search_term}'.", file=sys.stderr)


if __name__ == "__main__":
    main()