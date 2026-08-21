import os
import json
import boto3
from botocore.exceptions import ClientError
from ..utils.logging import get_logger

logger = get_logger("BedrockClient")

class BedrockClient:
    def __init__(self):
        bedrock_region = os.environ.get("BEDROCK_REGION", "us-east-1")
        self.model_id = os.environ.get("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0")
        
        try:
            self.client = boto3.client("bedrock-runtime", region_name=bedrock_region)
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            self.client = None

    def invoke_model(self, system_prompt: str, user_prompt: str) -> dict:
        """
        Invoke Bedrock using the Converse API for model-agnostic behavior.
        Works with both Amazon Nova and Anthropic Claude models.
        """
        if not self.client:
            raise ValueError("Bedrock client is not initialized")

        logger.info("Configured BEDROCK_MODEL_ID: %s", os.environ.get("BEDROCK_MODEL_ID"))
        logger.info("Invoking Bedrock model: %s", self.model_id)

        import botocore
        logger.info("Bedrock region: %s", self.client.meta.region_name if self.client else "unknown")
        logger.info("Bedrock model ID repr: %r", self.model_id)
        logger.info("Bedrock model ID length: %d", len(self.model_id))
        
        logger.info("boto3 version: %s", boto3.__version__)
        logger.info("botocore version: %s", botocore.__version__)

        try:
            response = self.client.converse(
                modelId=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": user_prompt}]
                    }
                ],
                system=[{"text": system_prompt}],
                inferenceConfig={
                    "maxTokens": 4096,
                    "temperature": 0.3
                }
            )
            
            return response["output"]["message"]["content"][0]["text"]
            
        except ClientError as e:
            logger.error(f"Bedrock invocation failed: {e}")
            raise
