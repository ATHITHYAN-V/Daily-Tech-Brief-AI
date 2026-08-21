import os
import json
import boto3
from botocore.exceptions import ClientError
from ..utils.logging import get_logger

logger = get_logger("BedrockClient")

class BedrockClient:
    def __init__(self):
        region = os.environ.get("AWS_REGION", "us-east-1")
        self.model_id = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")
        
        try:
            self.client = boto3.client("bedrock-runtime", region_name=region)
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            self.client = None

    def invoke_model(self, system_prompt: str, user_prompt: str) -> dict:
        """
        Invoke Bedrock with Claude 3/3.5 Messages API format.
        Will need modification if switching to Nova, but Claude 3/3.5 is the fallback/primary.
        """
        if not self.client:
            raise ValueError("Bedrock client is not initialized")

        logger.info(f"Invoking Bedrock model: {self.model_id}")

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": 0.3
        }

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response.get('body').read())
            
            if 'content' in response_body and len(response_body['content']) > 0:
                return response_body['content'][0]['text']
            
            return None
            
        except ClientError as e:
            logger.error(f"Bedrock invocation failed: {e}")
            raise
