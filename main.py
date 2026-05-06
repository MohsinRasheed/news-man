import logging
from src.fetch.rss_fetcher import RSSFetcher
from src.process.extractor import ArticleExtractor

# Configure logging for professional monitoring
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

def run_pipeline():
    # 1. Initialize Ingestion Engine
    # Using BBC World News as a stable data source for business intelligence
    feeds = ["http://feeds.bbci.co.uk/news/world/rss.xml"]
    fetcher = RSSFetcher(feeds)
    
    LOGGER.info("Starting Ingestion Phase...")
    raw_articles = fetcher.fetch_articles()
    
    if not raw_articles:
        LOGGER.warning("No articles found. Check internet connection or RSS URLs.")
        return

    # 2. Initialize Extraction Engine
    extractor = ArticleExtractor()
    processed_articles = []

    LOGGER.info(f"Processing {len(raw_articles[:5])} articles for full-text extraction...")

    # For testing, we only process the first 5 to save time/resources
    for entry in raw_articles[:5]:
        LOGGER.info(f"Extracting: {entry['title']}")
        
        # Step 5: Inject extractor into the flow
        full_data = extractor.extract(entry["link"])
        
        if full_data and full_data.get("text"):
            # Use the high-fidelity full text for future AI analysis
            entry["content"] = full_data["text"]
            entry["keywords"] = full_data.get("keywords", [])
        else:
            # Fallback to the RSS summary if extraction fails
            LOGGER.warning(f"Extraction failed for {entry['link']}. Using fallback summary.")
            entry["content"] = entry["clean_summary"]
            entry["keywords"] = []

        processed_articles.append(entry)

    # 3. Output Results (Phase 3 Verification)
    print("\n" + "="*50)
    print(" PIPELINE VERIFICATION REPORT ")
    print("="*50)
    for i, a in enumerate(processed_articles, 1):
        print(f"\n[{i}] {a['title']}")
        print(f"    Source: {a['source']}")
        print(f"    Content Length: {len(a['content'])} characters")
        print(f"    Top Keywords: {', '.join(a['keywords'][:5]) if a['keywords'] else 'None'}")
    print("\n" + "="*50)

if __name__ == "__main__":
    run_pipeline()