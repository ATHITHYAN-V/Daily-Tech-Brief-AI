import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict
from ..utils.logging import get_logger

logger = get_logger("NewsCleaner")

def filter_stale_and_invalid(articles: List[Dict]) -> List[Dict]:
    """
    Remove articles older than NEWS_MAX_AGE_HOURS and malformed articles.
    """
    max_age_hours = int(os.environ.get("NEWS_MAX_AGE_HOURS", 48))
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=max_age_hours)
    
    valid_articles = []
    
    for article in articles:
        if not article.get('title') or not article.get('url'):
            continue
            
        try:
            # Parse ISO 8601 string back to datetime
            published = datetime.fromisoformat(article['published_at'])
            if published < cutoff:
                continue # Too old
            if published > now + timedelta(hours=1):
                continue # In the future (with small buffer)
        except ValueError:
            continue # Invalid date format
            
        valid_articles.append(article)
        
    logger.info(f"Filtered {len(articles)} down to {len(valid_articles)} valid/recent articles")
    return valid_articles
