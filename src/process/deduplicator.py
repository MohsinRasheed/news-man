"""Utilities for removing duplicate articles by title similarity."""

from __future__ import annotations

from collections import Counter
from math import sqrt
import re
from typing import Any, Iterable

_SIMILARITY_THRESHOLD = 0.6
_TOKEN_RE = re.compile(r"[\w']+")


def remove_duplicates(articles: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return articles with near-duplicate titles removed.

    Titles are compared with cosine similarity over token-frequency vectors. When
    two titles have a similarity greater than 0.8, the article with the longer
    content body is kept.
    """
    cleaned: list[dict[str, Any]] = []

    for article in articles:
        duplicate_index = _find_duplicate_index(article, cleaned)

        if duplicate_index is None:
            cleaned.append(article)
            continue

        if _content_length(article) > _content_length(cleaned[duplicate_index]):
            cleaned[duplicate_index] = article

    return cleaned


def _find_duplicate_index(
    article: dict[str, Any], candidates: list[dict[str, Any]]
) -> int | None:
    """Return the index of the first candidate duplicate, if any."""
    title = _article_title(article)
    if not title:
        return None

    for index, candidate in enumerate(candidates):
        candidate_title = _article_title(candidate)
        if not candidate_title:
            continue

        if _title_similarity(title, candidate_title) > _SIMILARITY_THRESHOLD:
            return index

    return None


def _title_similarity(first_title: str, second_title: str) -> float:
    """Calculate cosine similarity between two article titles."""
    first_vector = _title_vector(first_title)
    second_vector = _title_vector(second_title)

    if not first_vector or not second_vector:
        return 0.0

    common_tokens = first_vector.keys() & second_vector.keys()
    dot_product = sum(first_vector[token] * second_vector[token] for token in common_tokens)
    first_magnitude = sqrt(sum(count * count for count in first_vector.values()))
    second_magnitude = sqrt(sum(count * count for count in second_vector.values()))

    if first_magnitude == 0 or second_magnitude == 0:
        return 0.0

    return dot_product / (first_magnitude * second_magnitude)


def _title_vector(title: str) -> Counter[str]:
    """Tokenize a title into a case-insensitive frequency vector."""
    return Counter(token.lower() for token in _TOKEN_RE.findall(title))


def _article_title(article: dict[str, Any]) -> str:
    """Read an article title, defaulting safely when the field is missing."""
    return str(article.get("title") or "")


def _content_length(article: dict[str, Any]) -> int:
    """Return the length of the article body used to choose the detailed copy."""
    content = article.get("content") or article.get("text") or ""
    return len(str(content))
