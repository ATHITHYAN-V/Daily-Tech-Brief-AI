import os
import json
import boto3
from botocore.exceptions import ClientError
from ..utils.logging import get_logger

logger = get_logger("S3Storage")

class S3Storage:
    def __init__(self):
        self.bucket = os.environ.get("S3_BUCKET", "daily-tech-brief-content")
        self.prefix = os.environ.get("EPISODE_PREFIX", "episodes")
        
        try:
            self.client = boto3.client("s3")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            self.client = None

    def upload_json(self, key: str, data: dict):
        if not self.client:
            raise ValueError("S3 client is not initialized")
            
        logger.info(f"Uploading JSON to s3://{self.bucket}/{key}")
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(data, indent=2),
                ContentType="application/json"
            )
        except ClientError as e:
            logger.error(f"Failed to upload JSON to S3: {e}")
            raise

    def upload_mp3(self, key: str, audio_bytes: bytes):
        if not self.client:
            raise ValueError("S3 client is not initialized")
            
        logger.info(f"Uploading MP3 to s3://{self.bucket}/{key}")
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=audio_bytes,
                ContentType="audio/mpeg"
            )
        except ClientError as e:
            logger.error(f"Failed to upload MP3 to S3: {e}")
            raise

def publish_episode(date: str, briefing_data: dict, audio_bytes: bytes, metadata: dict):
    storage = S3Storage()
    
    base_path = f"{storage.prefix}/{date}"
    
    mp3_key = f"{base_path}/briefing.mp3"
    stories_key = f"{base_path}/stories.json"
    transcript_key = f"{base_path}/transcript.json"
    meta_key = f"{base_path}/metadata.json"
    
    # We split briefing data logically for the frontend
    stories_data = {
        "date": date,
        "stories": briefing_data["stories"]
    }
    
    transcript_data = {
        "date": date,
        "opening": briefing_data["opening"],
        "closing": briefing_data["closing"],
        "full_script": briefing_data["full_script"]
    }
    
    # Upload everything
    if audio_bytes:
        storage.upload_mp3(mp3_key, audio_bytes)
    
    storage.upload_json(stories_key, stories_data)
    storage.upload_json(transcript_key, transcript_data)
    storage.upload_json(meta_key, metadata)
    
    # Update latest.json pointer
    latest_data = {
        "date": date,
        "title": f"Daily Tech Brief \u2014 {date}",
        "audio": mp3_key if audio_bytes else None,
        "stories": stories_key,
        "transcript": transcript_key
    }
    
    storage.upload_json("latest.json", latest_data)
    logger.info("Successfully published episode and updated latest.json")
