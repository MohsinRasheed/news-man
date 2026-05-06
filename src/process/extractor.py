"""Article extraction utilities using newspaper3k."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
import logging

from newspaper import Article, Config

LOGGER = logging.getLogger(__name__)

class ArticleExtractor:
    """Extract article metadata and content from a URL."""

    def __init__(self, timeout: int = 15) -> None:
        self.timeout = timeout
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )

    def extract(self, url: str) -> Optional[dict[str, Any]]:
        """Extract article details from a URL using NLP for enrichment."""
        try:
            config = Config()
            config.browser_user_agent = self.user_agent
            config.request_timeout = self.timeout

            article = Article(url=url, config=config)
            article.download()
            article.parse()
            
            # CRITICAL: This generates keywords and the summary
            # It requires the 'lxml_html_clean' and NLTK data to be present
            article.nlp() 

            publish_date = article.publish_date
            if isinstance(publish_date, datetime):
                publish_date = publish_date.isoformat()

            return {
                "title": article.title or None,
                "text": article.text or None,
                "authors": article.authors or [],
                "publish_date": publish_date,
                "top_image": article.top_image or None,
                "keywords": article.keywords or [],   # Added from NLP
                "summary": article.summary or None    # Added from NLP
            }
        except Exception as e:
            LOGGER.error(f"Extraction failed for {url}: {str(e)}")
            return None


if __name__ == "__main__":
    # Test with a specific article rather than a landing page for better results
    sample_url = "https://www.reuters.com/world/middle-east/israel-strikes-lebanon-after-hezbollah-rocket-fire-2024-05-06/"
    extractor = ArticleExtractor()
    result = extractor.extract(sample_url)

    if result is None:
        print("Extraction failed.")
    else:
        print("Extraction succeeded:")
        print(f"Title: {result['title']}")
        print(f"Keywords: {result['keywords']}")
        print(f"Summary Snippet: {result['summary'][:150]}...")