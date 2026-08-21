import os
import boto3
from botocore.exceptions import ClientError
from ..utils.logging import get_logger

logger = get_logger("PollyAudio")

class PollyClient:
    def __init__(self):
        region = os.environ.get("AWS_REGION", "us-east-1")
        self.voice_id = os.environ.get("POLLY_VOICE_ID", "Matthew")
        self.engine = os.environ.get("POLLY_ENGINE", "neural")
        
        try:
            self.client = boto3.client("polly", region_name=region)
        except Exception as e:
            logger.error(f"Failed to initialize Polly client: {e}")
            self.client = None

    def synthesize_speech(self, text: str) -> bytes:
        """
        Generate MP3 audio from text using Polly Neural Newscaster.
        """
        if not self.client:
            raise ValueError("Polly client is not initialized")

        logger.info(f"Synthesizing speech with Polly (Voice: {self.voice_id}, Engine: {self.engine})")

        # Wrap text in SSML to enable the newscaster domain if using Matthew or Joanna
        # The newscaster domain requires the neural engine
        if self.engine == "neural" and self.voice_id in ["Matthew", "Joanna"]:
            # Need to escape ampersands, angle brackets for valid XML/SSML
            escaped_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            ssml_text = f"""<speak>
<amazon:domain name="news">
{escaped_text}
</amazon:domain>
</speak>"""
            text_type = "ssml"
            input_text = ssml_text
        else:
            text_type = "text"
            input_text = text

        try:
            response = self.client.synthesize_speech(
                Text=input_text,
                TextType=text_type,
                OutputFormat='mp3',
                VoiceId=self.voice_id,
                Engine=self.engine
            )
            
            if 'AudioStream' in response:
                return response['AudioStream'].read()
            else:
                raise ValueError("No AudioStream in Polly response")
                
        except ClientError as e:
            logger.error(f"Polly synthesis failed: {e}")
            raise

def generate_audio(script: str) -> bytes:
    client = PollyClient()
    return client.synthesize_speech(script)
