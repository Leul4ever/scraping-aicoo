"""Entry point for AI COO E-commerce Data Acquisition Engine.
Orchestrates scraping, validates product data schemas via Pydantic,
and writes structured JSON datasets for downstream AI analysis.
"""

import argparse
import json
import logging
import os
import sys
from typing import List

from models import ProductCandidate, ScrapingBatchResult
from scraper import AliExpressScraper

# Set up root logger formatting
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("aicoo.main")


def print_product_summary(products: List[ProductCandidate]) -> None:
    """Print a clean visual summary of parsed products in the console."""
    if not products:
        print("\nNo product records found to display.\n")
        return

    print("\n" + "=" * 90)
    print(f"{'#':<4} {'ITEM ID':<18} {'PRICE':<10} {'RATING':<8} {'TITLE'[:45]:<45}")
    print("=" * 90)
    for idx, p in enumerate(products, 1):
        clean_title = (p.title[:42] + "...") if len(p.title) > 45 else p.title
        price_str = f"${p.price:.2f}"
        rating_str = f"{p.rating:.1f}/5"
        # Encode safely for Windows terminal
        line = f"{idx:<4} {str(p.item_id):<18} {price_str:<10} {rating_str:<8} {clean_title:<45}"
        try:
            print(line)
        except UnicodeEncodeError:
            print(line.encode("ascii", errors="replace").decode("ascii"))
    print("=" * 90 + "\n")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for custom scraping tasks."""
    parser = argparse.ArgumentParser(
        description="AI COO E-commerce Scraper: Acquire and normalize product listing candidates."
    )
    parser.add_argument(
        "--query",
        type=str,
        default="under-sink organizer",
        help="Search query or product category (default: 'under-sink organizer')",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of listing pages to scrape (default: 1)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="scraped_products.json",
        help="File path to save JSON results (default: 'scraped_products.json')",
    )
    parser.add_argument(
        "--proxy",
        type=str,
        default=None,
        help="Optional HTTP/HTTPS proxy URL override (e.g., 'http://user:pass@host:port')",
    )
    parser.add_argument(
        "--country",
        type=str,
        default="US",
        help="Target market country code (default: 'US')",
    )
    parser.add_argument(
        "--currency",
        type=str,
        default="USD",
        help="Target currency code (default: 'USD')",
    )
    parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="Disable mock candidate fallback on bot detection / network failures",
    )
    return parser.parse_args()


def main() -> int:
    """Execute scraping pipeline and serialize outputs."""
    args = parse_arguments()

    logger.info("Initializing AI COO Data Acquisition Engine...")
    logger.info("Target Category : '%s'", args.query)
    logger.info("Target Market   : %s (%s)", args.country, args.currency)
    logger.info("Target Pages    : %d", args.pages)
    logger.info("Output Destination: %s", args.output)

    scraper = AliExpressScraper(
        proxy_url=args.proxy,
        target_country=args.country,
        currency=args.currency,
        enable_mock_fallback=not args.no_fallback,
    )

    try:
        raw_candidates = scraper.search_all(query=args.query, max_pages=args.pages)
    except Exception as e:
        logger.error("Scraping execution halted with an unhandled error: %s", e)
        return 1

    # Schema validation through Pydantic container model
    batch_result = ScrapingBatchResult(
        query=args.query,
        target_market=args.country,
        total_found=len(raw_candidates),
        products=raw_candidates,
    )

    # Save to disk
    try:
        output_data = batch_result.model_dump(mode="json")
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logger.info("Successfully serialized %d products to '%s'.", len(batch_result.products), args.output)
    except IOError as e:
        logger.error("Failed to write output to file '%s': %s", args.output, e)
        return 1

    # Print summary visualization
    print_product_summary(batch_result.products)
    logger.info("Pipeline run finished successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
