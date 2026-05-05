"""Article extraction utilities using newspaper3k."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from newspaper import Article, Config


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
        """Extract article details from a URL.

        Returns:
            A dictionary with title, full text, authors, publish date, and top image,
            or None when extraction fails.
        """
        try:
            config = Config()
            config.browser_user_agent = self.user_agent
            config.request_timeout = self.timeout

            article = Article(url=url, config=config)
            article.download()
            article.parse()

            publish_date = article.publish_date
            if isinstance(publish_date, datetime):
                publish_date = publish_date.isoformat()

            return {
                "title": article.title or None,
                "text": article.text or None,
                "authors": article.authors or [],
                "publish_date": publish_date,
                "top_image": article.top_image or None,
            }
        except Exception:
            return None


if __name__ == "__main__":
    sample_url = "https://www.reuters.com/world/"
    extractor = ArticleExtractor()
    result = extractor.extract(sample_url)

    if result is None:
        print("Extraction failed.")
    else:
        print("Extraction succeeded:")
        print(result)
