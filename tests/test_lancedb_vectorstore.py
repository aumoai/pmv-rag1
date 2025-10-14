from collections.abc import Iterator

import pytest

from pmv_rag1.config import Config
from pmv_rag1.retriever.vectorstore import VectorStore
from pmv_rag1.services.gemini_client import GeminiClient


def _embedding_for_text(text: str) -> list[float]:
    length = float(len(text))
    char_sum = float(sum(ord(char) for char in text))
    return [length, char_sum % 97, (length + char_sum) % 53]


@pytest.fixture()
def lance_vector_store(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> Iterator[VectorStore]:
    tmp_dir = tmp_path_factory.mktemp("lancedb")
    monkeypatch.setattr(Config, "VECTOR_STORE_TYPE", "lancedb")
    monkeypatch.setattr(Config, "LANCEDB_URI", str(tmp_dir))
    monkeypatch.setattr(Config, "LANCEDB_TABLE_NAME", "test_documents")

    def _fake_init(self: GeminiClient) -> None:  # pragma: no cover - fixture setup
        self.client = None
        self.chat_model = "test-model"
        self.embedding_model = "test-embedding"
        self.chat_history = []

    monkeypatch.setattr(GeminiClient, "__init__", _fake_init, raising=False)

    async def _fake_get_embeddings(self: GeminiClient, texts: list[str]) -> list[list[float]]:
        return [_embedding_for_text(text) for text in texts]

    monkeypatch.setattr(GeminiClient, "get_embeddings", _fake_get_embeddings, raising=False)

    yield VectorStore()


@pytest.mark.asyncio
async def test_lancedb_add_and_similarity_search(lance_vector_store: VectorStore) -> None:
    vector_store = lance_vector_store

    await vector_store.add_documents(["alpha document"], {"category": "alpha", "id": "1"})
    await vector_store.add_documents(["beta document"], {"category": "beta", "id": "2"})

    results = await vector_store.similarity_search("alpha document", k=2)

    assert results
    assert results[0]["page_content"] == "alpha document"
    assert results[0]["metadata"] == {"category": "alpha", "id": "1"}


@pytest.mark.asyncio
async def test_lancedb_similarity_search_with_filter(lance_vector_store: VectorStore) -> None:
    vector_store = lance_vector_store

    await vector_store.add_documents(["gamma file"], {"category": "gamma", "id": "3"})
    await vector_store.add_documents(["delta file"], {"category": "delta", "id": "4"})

    results = await vector_store.similarity_search_with_filter(
        "file", {"category": "delta"}, k=3
    )

    assert results
    assert all(result["metadata"]["category"] == "delta" for result in results)
    assert {result["page_content"] for result in results} == {"delta file"}


@pytest.mark.asyncio
async def test_lancedb_delete_by_metadata(lance_vector_store: VectorStore) -> None:
    vector_store = lance_vector_store

    await vector_store.add_documents(["epsilon report"], {"category": "epsilon", "id": "5"})
    await vector_store.add_documents(["zeta report"], {"category": "zeta", "id": "6"})

    await vector_store.delete_by_metadata({"category": "epsilon"})

    stats = await vector_store.get_collection_stats()
    assert stats["document_count"] == 1
    assert stats["collection_name"] == "test_documents"

    results = await vector_store.similarity_search("report", k=2)
    remaining_categories = {result["metadata"].get("category") for result in results}
    assert remaining_categories == {"zeta"}
