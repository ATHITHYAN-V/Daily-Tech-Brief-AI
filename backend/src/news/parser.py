import time
from datetime import datetime, timezone
from bs4 import BeautifulSoup

def parse_date(entry) -> datetime:
    """Attempt to parse date from various feedparser fields."""
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        return datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
    if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        return datetime.fromtimestamp(time.mktime(entry.updated_parsed), tz=timezone.utc)
    # Fallback to current time if feed is malformed but has an entry
    return datetime.now(timezone.utc)

def clean_html(raw_html: str) -> str:
    """Remove HTML tags from description."""
    if not raw_html:
        return ""
    try:
        soup = BeautifulSoup(raw_html, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    except Exception:
        return raw_html

def parse_entry(entry, source_name: str, category: str) -> dict:
    """Normalize a feedparser entry into our standard dictionary."""
    
    title = entry.get('title', '').strip()
    link = entry.get('link', '').strip()
    
    # Try description then summary
    description = entry.get('summary', entry.get('description', ''))
    clean_desc = clean_html(description)
    
    # Limit description length to avoid excessive token usage
    if len(clean_desc) > 1000:
        clean_desc = clean_desc[:997] + "..."

    published_at = parse_date(entry)
    
    return {
        "title": title,
        "source": source_name,
        "url": link,
        "published_at": published_at.isoformat(),
        "description": clean_desc,
        "category": category
    }
