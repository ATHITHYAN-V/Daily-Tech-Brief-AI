import os
import boto3
from botocore.exceptions import ClientError
import re
from ..utils.logging import get_logger

logger = get_logger("PollyAudio")

def chunk_text(text: str, max_length: int = 2500) -> list[str]:
    """
    Split text safely into chunks < max_length.
    Prefers splitting at paragraphs (\n\n), then sentences (.), then spaces.
    """
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    
    # Split by double newline (paragraphs)
    paragraphs = text.split('\n\n')
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= max_length:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
        else:
            # Paragraph itself is too big or doesn't fit in current chunk
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            
            if len(para) <= max_length:
                current_chunk = para
            else:
                # Need to split the paragraph by sentences
                sentences = re.split(r'(?<=[.!?]) +', para)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 1 <= max_length:
                        if current_chunk:
                            current_chunk += " " + sentence
                        else:
                            current_chunk = sentence
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = ""
                        
                        if len(sentence) <= max_length:
                            current_chunk = sentence
                        else:
                            # Sentence is too long, split by words
                            words = sentence.split(' ')
                            for word in words:
                                if len(current_chunk) + len(word) + 1 <= max_length:
                                    if current_chunk:
                                        current_chunk += " " + word
                                    else:
                                        current_chunk = word
                                else:
                                    if current_chunk:
                                        chunks.append(current_chunk.strip())
                                    current_chunk = word
                                    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
        
    return chunks

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

        chunks = chunk_text(text, max_length=2500)
        logger.info(f"Total transcript characters: {len(text)}")
        logger.info(f"Number of Polly chunks: {len(chunks)}")

        audio_chunks = []
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Synthesizing Polly chunk {i}/{len(chunks)} ({len(chunk)} characters)")
            
            # Wrap text in SSML to enable the newscaster domain if using Matthew or Joanna
            # The newscaster domain requires the neural engine
            if self.engine == "neural" and self.voice_id in ["Matthew", "Joanna"]:
                # Need to escape ampersands, angle brackets for valid XML/SSML
                escaped_text = chunk.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                ssml_text = f"<speak>\n<amazon:domain name=\"news\">\n{escaped_text}\n</amazon:domain>\n</speak>"
                text_type = "ssml"
                input_text = ssml_text
            else:
                text_type = "text"
                input_text = chunk

            try:
                response = self.client.synthesize_speech(
                    Text=input_text,
                    TextType=text_type,
                    OutputFormat='mp3',
                    VoiceId=self.voice_id,
                    Engine=self.engine
                )
                
                if 'AudioStream' in response:
                    audio_chunks.append(response['AudioStream'].read())
                    logger.info(f"Polly chunk {i} successful")
                else:
                    raise ValueError(f"No AudioStream in Polly response for chunk {i}")
                    
            except ClientError as e:
                logger.error(f"Polly synthesis failed at chunk {i}: {e}")
                raise
        
        final_audio = b"".join(audio_chunks)
        logger.info(f"Final MP3 size: {len(final_audio)} bytes")
        return final_audio

def generate_audio(script: str) -> bytes:
    client = PollyClient()
    return client.synthesize_speech(script)
