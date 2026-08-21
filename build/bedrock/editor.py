import os
from typing import List, Dict, Optional
from ..utils.logging import get_logger
from .client import BedrockClient
from .prompts import SYSTEM_PROMPT, build_user_prompt
from .validator import validate_and_parse_json

logger = get_logger("BedrockEditor")

def generate_briefing(date: str, articles: List[Dict]) -> Optional[Dict]:
    """
    Pass the cleaned, deduplicated articles to Bedrock to select the Top 10
    and generate the radio script.
    """
    max_articles = int(os.environ.get("MAX_ARTICLES_TO_MODEL", 30))
    
    # We slice to avoid exceeding token limits. The cleaner/deduplicator 
    # should hopefully have ordered them somewhat, but here we just take the first N.
    # A more advanced version might pre-rank, but for now we just take the newest N.
    # Ensure they are sorted by date descending just in case.
    articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
    candidates = articles[:max_articles]
    
    logger.info(f"Sending {len(candidates)} candidate stories to Bedrock")
    
    client = BedrockClient()
    user_prompt = build_user_prompt(date, candidates)
    
    # Retry logic (1 retry as specified in requirements)
    for attempt in range(2):
        try:
            logger.info(f"Bedrock generation attempt {attempt + 1}...")
            response_text = client.invoke_model(SYSTEM_PROMPT, user_prompt)
            briefing_data = validate_and_parse_json(response_text)
            
            logger.info("Successfully generated and validated briefing JSON")
            return briefing_data
            
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt == 1:
                logger.error("All Bedrock generation attempts failed.")
                return None
