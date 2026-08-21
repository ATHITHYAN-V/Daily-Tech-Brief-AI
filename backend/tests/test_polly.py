import pytest
from src.audio.polly import chunk_text

def test_chunk_text_short():
    text = "Hello world."
    chunks = chunk_text(text, 100)
    assert len(chunks) == 1
    assert chunks[0] == "Hello world."

def test_chunk_text_paragraphs():
    # Two paragraphs that are 50 chars each, max length is 60.
    # Should split into two chunks.
    para1 = "A" * 50
    para2 = "B" * 50
    text = f"{para1}\n\n{para2}"
    chunks = chunk_text(text, 60)
    assert len(chunks) == 2
    assert chunks[0] == para1
    assert chunks[1] == para2

def test_chunk_text_sentences():
    # A single paragraph with two sentences. Max length is 60.
    # Sentences are 40 chars each.
    sent1 = "A" * 39 + "."
    sent2 = "B" * 39 + "."
    text = f"{sent1} {sent2}"
    chunks = chunk_text(text, 60)
    assert len(chunks) == 2
    assert chunks[0] == sent1
    assert chunks[1] == sent2

def test_chunk_text_words():
    # A single sentence with two words. Max length is 60.
    # Words are 40 chars each.
    word1 = "A" * 40
    word2 = "B" * 40
    text = f"{word1} {word2}."
    chunks = chunk_text(text, 60)
    assert len(chunks) == 2
    assert chunks[0] == word1
    assert chunks[1] == word2 + "."

def test_chunk_text_no_words_cut():
    word = "A" * 10
    text = f"{word} {word} {word}"
    chunks = chunk_text(text, 15)
    # Each chunk should contain exactly one word, without cutting any.
    assert len(chunks) == 3
    assert chunks[0] == word
    assert chunks[1] == word
    assert chunks[2] == word

def test_chunk_text_preserves_content():
    # A mix of paragraphs and sentences.
    text = "Hello there. How are you?\n\nI am fine. This is a longer sentence to force wrapping across boundaries."
    chunks = chunk_text(text, 25)
    # The concatenated chunks with space or newline re-added should be identical to the original,
    # or at least contain exactly the same words in order.
    # Our chunk_text function drops the connecting spaces/newlines when they straddle chunk boundaries,
    # but the Polly synthesis does not care about inter-chunk spacing.
    # Let's verify no words are dropped.
    import re
    original_words = re.findall(r'\S+', text)
    chunked_words = []
    for chunk in chunks:
        chunked_words.extend(re.findall(r'\S+', chunk))
        assert len(chunk) <= 25
    assert original_words == chunked_words
