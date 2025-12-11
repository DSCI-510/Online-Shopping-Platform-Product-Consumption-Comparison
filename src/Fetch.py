import re
import os
import time
import random
import csv
import json
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

# random User-Agent pool
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
]

def get_headers() -> Dict[str, str]:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
    }

def fetch_html(url: str) -> Optional[str]:
    try:
        resp = requests.get(url, headers=get_headers(), timeout=20)
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return None

def parse_price_from_block(block) -> Optional[float]:
    price_li = block.select_one("li.price-current")
    if price_li:
        strong = price_li.select_one("strong")
        sup = price_li.select_one("sup")
        if strong:
            main = strong.get_text(strip=True)
            frac = sup.get_text(strip=True) if sup else "00"
            num_str = (main + frac).replace(",", "")
            try:
                return float(num_str[:-2] + "." + num_str[-2:])
            except ValueError:
                pass
    
    price_block = block.select_one(".item-action .price-area")
    search_scope = price_block.get_text() if price_block else block.get_text()
    m = re.search(r"\$\s*([\d,]+\.\d{2})", search_scope)
    if not m:
        m = re.search(r"\$\s*([\d,]+)", search_scope)
    if m:
        price_str = m.group(1).replace(",", "")
        try:
            return float(price_str)
        except ValueError:
            pass
            
    price_block_div = block.select_one("div.item-cell[data-price]")
    if price_block_div and price_block_div.get("data-price"):
        try:
            return float(price_block_div["data-price"])
        except ValueError:
            pass
    return None

def parse_rating_and_reviews(block) -> tuple[Optional[float], Optional[int]]:
    rating = None
    reviews = None
    rating_i = block.select_one("i.rating")
    if rating_i:
        aria_label = rating_i.get("aria-label") 
        if aria_label:
            m_float = re.search(r"Rated\s+([\d\.]+)\s+out", aria_label, re.IGNORECASE)
            if m_float:
                try:
                    rating = float(m_float.group(1))
                except ValueError:
                    pass
        if rating is None:
            cls = " ".join(rating_i.get("class", []))
            m_int = re.search(r"rating-(\d)", cls)
            if m_int:
                try:
                    rating = float(m_int.group(1))
                except ValueError:
                    pass

    reviews_span = block.select_one("span.item-rating-num")
    if reviews_span:
        m = re.search(r"\(([\d,]+)\)", reviews_span.get_text(strip=True))
        if m:
            reviews = int(m.group(1).replace(",", ""))
    return rating, reviews

def parse_search_page(html: str, keyword: str) -> tuple[List[Dict], Optional[int]]:
    soup = BeautifulSoup(html, "html.parser")
    results: List[Dict] = []
    total_pages: Optional[int] = None

    page_nav_span = soup.select_one("div.list-wrap nav.pagination span.page-title")
    if page_nav_span:
        text = page_nav_span.get_text(strip=True)
        m = re.search(r"of\s+(\d+)", text)
        if m:
            try:
                total_pages = int(m.group(1))
            except ValueError:
                pass
    
    items = soup.select("div.item-cell")
    for item in items:
        title_a = item.select_one("a.item-title")
        if not title_a:
            continue
        
        title = title_a.get_text(strip=True)
        product_url = title_a.get("href", "")
        price = parse_price_from_block(item)
        rating, review_count = parse_rating_and_reviews(item)
        ship = item.select_one("li.price-ship")
        shipping = ship.get_text(strip=True) if ship else ""

        brand_a = item.select_one("a.item-brand img")
        brand = None
        if brand_a and brand_a.get("title"):
            brand = brand_a["title"]
        else:
            brand = title.split()[0]

        results.append({
            "title": title,
            "product_url": product_url,
            "brand": brand,
            "price": price,
            "rating": rating,
            "review_count": review_count,
            "shipping": shipping,
        })

    return results, total_pages

def save_to_csv(data: List[Dict], filename: str):
    if not data:
        print(f"[WARN] Data is empty, skipping CSV save.")
        return

    fieldnames = list(data[0].keys())
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f" === Data successfully saved to {filename} === ")
    except Exception as e:
        print(f"[ERROR] Failed to save CSV file {filename}: {e}")

def run_paginated_scraper(start_url: str, keyword: str, max_pages_limit: int = 0):
    all_results: List[Dict] = []
    current_page = 1
    max_pages: Optional[int] = None
    
    limit_info = f"(Limited to {max_pages_limit} pages)" if max_pages_limit > 0 else "(Full scan)"
    print(f" --- Starting Newegg scraper for keyword: '{keyword}' {limit_info} ---")

    raw_dir = "../data/raw/raw_html_data"
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)

    while True:
        if max_pages_limit > 0 and current_page > max_pages_limit:
            print(f" || Reached page limit ({max_pages_limit}). Stopping.")
            break
            
        url = start_url
        if current_page > 1:
            url = f"{start_url}&page={current_page}"
            
        print(f" - Fetching Page {current_page} (URL: {url}...)")
        
        html = fetch_html(url)
        if not html:
            print(" ! Failed to retrieve HTML. Stopping.")
            break

        raw_filename = os.path.join(raw_dir, f"Raw_{keyword.replace(' ', '_')}_p_{current_page}.html")
        with open(raw_filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"   > Saved raw HTML to {raw_filename}")

        #json_filename = os.path.join(raw_dir, f"Raw_{keyword.replace(' ', '_')}_p_{current_page}.json")
        #with open(json_filename, 'w', encoding='utf-8') as f:
        #    json.dump({"url": url, "html": html}, f)
        #print(f"   > Saved raw JSON to {json_filename}")
            
        page_results, parsed_total_pages = parse_search_page(html, keyword)
        
        if parsed_total_pages and max_pages is None:
            max_pages = parsed_total_pages
            print(f" -- Total pages detected: {max_pages} -- ")
            
        if not page_results:
            print("Error: No items found on this page. Stopping.")
            break
            
        all_results.extend(page_results)
        
        if max_pages is not None and current_page >= max_pages:
            print(" - Reached the last page reported by the site. Stopping.")
            break
            
        current_page += 1
        time.sleep(random.uniform(1.0, 3.0)) 

    return all_results

def run_fetch(keyword: str, output_path: str, output_base: str, page_limit: int):
    # url encode the keyword: transform spaces to '+'
    base_url = f"https://www.newegg.com/p/pl?d={keyword.replace(' ', '+')}"
    
    data = run_paginated_scraper(base_url, keyword, max_pages_limit=page_limit)

    data_dir = output_path
    
    if data:
        # name format of files: Raw_{base}_p{limit}.csv
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        csv_filename = os.path.join(data_dir, f"Raw_{output_base}_p{page_limit}.csv")
        print(f"\n --- Saving Data --- ")
        save_to_csv(data, csv_filename)
        print("="*80, "\n")
    else:
        print(f" ! No data fetched for {keyword}.")