import json
from ..utils.logging import get_logger

logger = get_logger("BedrockValidator")

def validate_and_parse_json(response_text: str) -> dict:
    """
    Ensure the Bedrock response is valid JSON and matches our expected structure.
    """
    if not response_text:
        raise ValueError("Empty response from Bedrock")
        
    try:
        # Sometimes models wrap JSON in markdown blocks even when told not to.
        # Cheap cleanup:
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        data = json.loads(text.strip())
        
        # Basic schema validation
        required_keys = ["episode_date", "opening", "stories", "closing", "full_script"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key in JSON output: {key}")
                
        if len(data["stories"]) == 0:
            raise ValueError("No stories selected in the output")
            
        story_keys = ["rank", "headline", "source", "url", "briefing_segment"]
        for story in data["stories"]:
            for sk in story_keys:
                if sk not in story:
                    raise ValueError(f"Story missing required key: {sk}")
                    
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from Bedrock: {e}\nRaw output: {response_text[:200]}...")
        raise
