# Pixel packages

Installable Python package `pixel` (provider interfaces and shared helpers).

| Module | Phase 2 role |
|---|---|
| `pixel.ai` | `LLMProvider`, `EmbeddingProvider` protocols |
| `pixel.voice` | STT/TTS protocols |
| `pixel.knowledge` | Placeholder — RAG is Phase 6 |
| `pixel.tools` | Placeholder — tools are Phase 7 |
| `pixel.security` | Fail-closed helpers |
| `pixel.observability` | Correlation IDs |
| `pixel.shared` | Env-name constants |

Vendor adapters live in `pixel.providers` (`mock`, `openai`). httpx is used only inside those adapters.
