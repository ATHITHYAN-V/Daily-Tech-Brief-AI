import feedparser
from typing import List, Dict, Tuple
from .sources import NEWS_SOURCES
from .parser import parse_entry
from ..utils.logging import get_logger

logger = get_logger("NewsFetcher")

def fetch_feeds() -> Tuple[List[Dict], Dict]:
    """
    Fetch all RSS feeds and return (articles, stats).
    """
    articles = []
    stats = {
        "sources_attempted": len(NEWS_SOURCES),
        "sources_successful": 0,
        "sources_failed": 0
    }

    for source in NEWS_SOURCES:
        try:
            logger.info(f"Fetching {source['name']}...")
            # We add timeout in a real world scenario, but feedparser handles basic connections
            feed = feedparser.parse(source['url'])
            
            if getattr(feed, 'bozo', 0) and not feed.entries:
                # Malformed feed without entries
                logger.warning(f"Failed to parse {source['name']}")
                stats["sources_failed"] += 1
                continue

            parsed_count = 0
            for entry in feed.entries:
                parsed = parse_entry(entry, source['name'], source['category'])
                if parsed['title'] and parsed['url']:
                    articles.append(parsed)
                    parsed_count += 1
            
            if parsed_count > 0:
                stats["sources_successful"] += 1
            else:
                logger.warning(f"No valid entries found for {source['name']}")
                stats["sources_failed"] += 1
                
        except Exception as e:
            logger.error(f"Error fetching {source['name']}: {str(e)}")
            stats["sources_failed"] += 1
            
    return articles, stats
