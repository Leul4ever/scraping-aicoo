# AI COO Data Acquisition Engine (`scraping-aicoo`)

A robust, production-grade web scraping and fallback engine for e-commerce platforms (AliExpress) tailored for AI-driven operations (AI COO). Designed to acquire high-potential product candidates for target categories (e.g., "under-sink organizer" in the US market) without relying on restricted official developer APIs.

---

## 📁 Project Architecture

```
scraping-aicoo/
├── main.py              # CLI entry point, batch pipeline orchestrator
├── scraper.py           # AliExpress crawler, session manager, rate limiter & parsers
├── models.py            # Pydantic data schemas (ProductCandidate, ScrapingBatchResult)
├── requirements.txt     # Python dependencies
├── .env.example         # Template for proxy and regional configuration
├── .gitignore           # Git ignore rules
└── scraped_products.json # Serialized batch output dataset
```

---

## 🛠️ Features

1. **Pydantic Data Validation:**
   - Guaranteed schema consistency for `item_id`, `title`, `price`, `currency`, `rating`, `review_count`, `product_url`, and `image_url`.
   - Cleanses price strings (e.g., `$19.99` -> `19.99`), limits rating bounds (0.0 to 5.0), and normalizes URLs.

2. **Resilient Scraping Strategies:**
   - **Market Localization:** Automatically configures US regional cookies (`aep_usuc_f` with `site=glo&c_tp=USD&region=US`) to guarantee USD pricing and US availability.
   - **Desktop Emulation:** Rotates realistic modern desktop User-Agents (`Chrome 128`, `Firefox 129`, etc.) and sets security headers (`Sec-Ch-Ua`, `Sec-Fetch-*`).
   - **Dual Parsing:** Parses embedded JSON state blobs (`window.runParams`, `itemList`) with fallback to BeautifulSoup HTML DOM card selectors.
   - **Rate Limiting & Jitter:** Configurable randomized sleep intervals between consecutive page requests.

3. **Proxy & Corporate Fallback Support:**
   - Supports standard residential/datacenter HTTP/HTTPS proxies via `.env` or `--proxy`.
   - Includes automatic high-fidelity fallback mock candidates when anti-bot challenges or offline testing environments are encountered, keeping downstream AI pipelines operational.

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env` and configure your proxy if required:
```bash
cp .env.example .env
```

### 3. Run the Scraper
Run with default category (`"under-sink organizer"`, US market):
```bash
python main.py
```

### 4. Custom Queries and CLI Options
```bash
# Query a custom product niche for 2 pages
python main.py --query "desk cable organizer" --pages 2

# Target a different output file
python main.py --query "bathroom shower caddy" --output caddies.json

# Route through a proxy
python main.py --proxy "http://username:password@proxy.example.com:8080"

# Disable fallback if strict live scraping is required
python main.py --no-fallback
```
