"""RSS fetching utility for news intelligence pipelines."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import logging
import re
from typing import Dict, Iterable, List, Optional

import feedparser
import requests


LOGGER = logging.getLogger(__name__)


@dataclass
class RSSFetcherConfig:
    """Configuration for RSSFetcher."""

    timeout_seconds: int = 10
    user_agent: str = "news-intel-rss-fetcher/1.0"


class RSSFetcher:
    """Fetch and normalize articles from one or more RSS feeds."""

    def __init__(self, feed_urls: Iterable[str], config: Optional[RSSFetcherConfig] = None) -> None:
        self.feed_urls = list(feed_urls)
        self.config = config or RSSFetcherConfig()
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": self.config.user_agent})

    @staticmethod
    def _strip_html(text: str) -> str:
        """Remove HTML tags and condense whitespace."""
        if not text:
            return ""
        text_no_tags = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", text_no_tags).strip()

    @staticmethod
    def _extract_published(entry: Dict) -> str:
        """Extract a best-effort publication date string."""
        if entry.get("published"):
            return entry["published"]
        if entry.get("updated"):
            return entry["updated"]

        for key in ("published_parsed", "updated_parsed"):
            if entry.get(key):
                return datetime(*entry[key][:6]).isoformat()

        return ""

    def _fetch_feed(self, url: str) -> List[Dict[str, str]]:
        """Fetch and parse a single RSS feed URL."""
        try:
            response = self._session.get(url, timeout=self.config.timeout_seconds)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            LOGGER.exception("Timeout while fetching RSS feed: %s", url)
            return []
        except requests.exceptions.RequestException:
            LOGGER.exception("Network error while fetching RSS feed: %s", url)
            return []

        try:
            parsed_feed = feedparser.parse(response.content)
        except Exception:
            LOGGER.exception("Failed to parse RSS feed content: %s", url)
            return []

        if getattr(parsed_feed, "bozo", False):
            LOGGER.warning("Invalid or malformed RSS feed skipped: %s", url)
            return []

        source = parsed_feed.feed.get("title", url)
        articles: List[Dict[str, str]] = []

        for entry in parsed_feed.entries:
            summary = entry.get("summary", "")
            articles.append(
                {
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", "").strip(),
                    "published_date": self._extract_published(entry),
                    "source": source,
                    "clean_summary": self._strip_html(summary),
                }
            )

        return articles

    def fetch_articles(self) -> List[Dict[str, str]]:
        """Fetch and parse articles from all configured feed URLs."""
        all_articles: List[Dict[str, str]] = []
        for url in self.feed_urls:
            if not url:
                LOGGER.warning("Encountered empty RSS URL; skipping.")
                continue
            all_articles.extend(self._fetch_feed(url))
        return all_articles


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    bbc_world_news_rss = "http://feeds.bbci.co.uk/news/world/rss.xml"
    fetcher = RSSFetcher([bbc_world_news_rss])
    results = fetcher.fetch_articles()

    print(f"Fetched {len(results)} articles from BBC World News.")
    for article in results[:3]:
        print("-" * 80)
        print(f"Title: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"Published: {article['published_date']}")
        print(f"Link: {article['link']}")
        print(f"Summary: {article['clean_summary'][:200]}...")
