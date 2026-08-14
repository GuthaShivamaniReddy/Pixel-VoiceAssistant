from pixel.ai import EmbeddingProvider, LLMProvider
from pixel.knowledge import VectorStoreProvider
from pixel.voice import SpeechToTextProvider, TextToSpeechProvider


def test_provider_protocols_are_importable() -> None:
    assert LLMProvider.__name__ == "LLMProvider"
    assert SpeechToTextProvider.__name__ == "SpeechToTextProvider"
    assert TextToSpeechProvider.__name__ == "TextToSpeechProvider"
    assert EmbeddingProvider.__name__ == "EmbeddingProvider"
    assert VectorStoreProvider.__name__ == "VectorStoreProvider"
