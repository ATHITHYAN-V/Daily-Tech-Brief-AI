import os
import uuid
from typing import Dict, Any

from .utils.logging import get_logger
from .utils.dates import get_current_utc_time, format_iso_time, format_date_only

from .news.fetcher import fetch_feeds
from .news.cleaner import filter_stale_and_invalid
from .news.deduplicator import deduplicate_articles
from .bedrock.editor import generate_briefing
from .audio.polly import generate_audio
from .storage.s3 import publish_episode

logger = get_logger("LambdaHandler")

def main_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point for Daily Tech Brief.
    """
    execution_id = str(uuid.uuid4())
    logger.info(f"[START] Execution ID: {execution_id}")
    
    mock_mode = os.environ.get("MOCK_MODE", "false").lower() == "true"
    if mock_mode:
        logger.info("Running in MOCK_MODE. Expected to be invoked locally via run_local_demo.py.")
    
    now = get_current_utc_time()
    today_date = format_date_only(now)
    generated_at = format_iso_time(now)
    
    # 1. Fetch
    raw_articles, stats = fetch_feeds()
    
    # 2. Clean
    cleaned_articles = filter_stale_and_invalid(raw_articles)
    
    # 3. Deduplicate (Deterministic)
    unique_articles = deduplicate_articles(cleaned_articles)
    
    logger.info(f"Sources: {stats['sources_attempted']} attempted, "
                f"{stats['sources_successful']} successful, "
                f"{stats['sources_failed']} failed")
                
    logger.info(f"Articles: {len(raw_articles)} collected, "
                f"{len(raw_articles) - len(unique_articles)} duplicates/invalid, "
                f"{len(unique_articles)} unique")
                
    if len(unique_articles) < 5:
        logger.warning("Very few articles found today. Proceeding anyway, but briefing will be short.")
        
    # 4. Bedrock
    if mock_mode:
        briefing_data = _get_mock_briefing(today_date)
    else:
        briefing_data = generate_briefing(today_date, unique_articles)
        
    if not briefing_data:
        logger.error("[COMPLETE] Failed to generate briefing from Bedrock.")
        return {"statusCode": 500, "body": "Bedrock generation failed"}
        
    logger.info(f"Bedrock: {len(unique_articles)} analyzed, {len(briefing_data.get('stories', []))} selected")
    script_words = len(briefing_data.get('full_script', '').split())
    logger.info(f"Script: {script_words} words")
    
    # 5. Polly
    audio_bytes = None
    audio_status = "unavailable"
    
    if mock_mode:
        logger.info("Polly: Mock audio generated")
        audio_bytes = b"mock audio bytes"
        audio_status = "success"
    else:
        try:
            audio_bytes = generate_audio(briefing_data['full_script'])
            logger.info("Polly: Audio generated")
            audio_status = "success"
        except Exception as e:
            logger.error(f"Polly: Audio generation failed: {e}")
            audio_status = "failed"
            
    # 6. Metadata
    metadata = {
        "date": today_date,
        "generated_at": generated_at,
        "duration_seconds": 0, # Could calculate if using a proper MP3 library, but fine to omit/mock
        "stories_count": len(briefing_data.get('stories', [])),
        "sources_count": stats['sources_attempted'],
        "articles_analyzed": len(raw_articles),
        "status": "success",
        "audio_status": audio_status,
        "audio_key": f"{os.environ.get('EPISODE_PREFIX', 'episodes')}/{today_date}/briefing.mp3" if audio_status == "success" else None
    }
    
    # 7. S3 Publish
    if mock_mode:
        logger.info("S3: Upload skipped in mock mode")
        _save_local_output(today_date, briefing_data, metadata)
    else:
        publish_episode(today_date, briefing_data, audio_bytes, metadata)
        logger.info("S3: Upload successful")
        
    logger.info("[COMPLETE] Execution finished successfully.")
    return {"statusCode": 200, "body": "Success"}
    
def _get_mock_briefing(date: str) -> dict:
    return {
        "episode_date": date,
        "opening": "Good morning. While you were away, the technology world moved again. Here are the top stories.",
        "stories": [
            {
                "rank": 1,
                "category": "AI",
                "headline": "Mock AI Story",
                "source": "Mock Source",
                "url": "https://example.com/mock",
                "importance_score": 95,
                "why_it_matters": "Mock matters",
                "briefing_segment": "Let's start with AI. A mock story happened."
            }
        ],
        "closing": "That's your Daily Tech Brief. We'll be back tomorrow.",
        "full_script": "Good morning. While you were away, the technology world moved again. Here are the top stories. Let's start with AI. A mock story happened. That's your Daily Tech Brief. We'll be back tomorrow."
    }

def _save_local_output(date: str, briefing_data: dict, metadata: dict):
    import json
    os.makedirs(f"local_output/{date}", exist_ok=True)
    
    with open(f"local_output/{date}/stories.json", "w") as f:
        json.dump({"date": date, "stories": briefing_data["stories"]}, f, indent=2)
        
    with open(f"local_output/{date}/transcript.json", "w") as f:
        json.dump({
            "date": date,
            "opening": briefing_data["opening"],
            "closing": briefing_data["closing"],
            "full_script": briefing_data["full_script"]
        }, f, indent=2)
        
    with open(f"local_output/{date}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
        
    with open(f"local_output/latest.json", "w") as f:
        json.dump({
            "date": date,
            "title": f"Daily Tech Brief - {date}",
            "audio": f"local_output/{date}/briefing.mp3",
            "stories": f"local_output/{date}/stories.json",
            "transcript": f"local_output/{date}/transcript.json"
        }, f, indent=2)
