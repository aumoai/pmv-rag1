from __future__ import annotations

import os

from pmv_rag1.config import Config
from pmv_rag1.services.gemini_client import GeminiClient

os.environ.setdefault("GEMINI_API_KEY", "test-key")
Config.GEMINI_API_KEY = "test-key"


def _default_fake_init(self: GeminiClient) -> None:  # pragma: no cover - test bootstrap
    self.client = None
    self.chat_model = "test-model"
    self.embedding_model = "test-embedding"
    self.chat_history = []


async def _default_fake_embeddings(self: GeminiClient, texts: list[str]) -> list[list[float]]:
    return [[float(index)] * 3 for index, _ in enumerate(texts)]


GeminiClient.__init__ = _default_fake_init  # type: ignore[assignment]
GeminiClient.get_embeddings = _default_fake_embeddings  # type: ignore[assignment]
