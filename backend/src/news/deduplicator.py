import urllib.parse
import re
from typing import List, Dict
from ..utils.logging import get_logger

logger = get_logger("NewsDeduplicator")

def normalize_url(url: str) -> str:
    """Remove tracking params and fragments from URL."""
    try:
        parsed = urllib.parse.urlparse(url)
        # Keep only the base path
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')
        return clean_url.lower()
    except Exception:
        return url.lower()

def normalize_title(title: str) -> str:
    """Lowercase and remove non-alphanumeric chars for comparison."""
    return re.sub(r'[^a-z0-9]', '', title.lower())

def deduplicate_articles(articles: List[Dict]) -> List[Dict]:
    """
    Remove exact duplicate URLs and extremely similar titles.
    Leaves semantic clustering to Bedrock.
    """
    seen_urls = set()
    seen_titles = set()
    unique_articles = []
    
    for article in articles:
        url_norm = normalize_url(article['url'])
        title_norm = normalize_title(article['title'])
        
        if url_norm in seen_urls:
            continue
            
        if title_norm in seen_titles:
            continue
            
        seen_urls.add(url_norm)
        seen_titles.add(title_norm)
        unique_articles.append(article)
        
    logger.info(f"Deduplication: {len(articles)} -> {len(unique_articles)} unique articles")
    return unique_articles
