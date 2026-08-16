"""Contract tests for the RAG legal_context payload.

The explain endpoint returns `legal_context` as a list of
{content, source, law, relevance_score} dicts. The frontend
(ExplainResponse in utils/api.ts) must type it exactly this way —
these tests pin the backend side of that contract so a silent
shape change here cannot silently break the UI again (audit B2).
"""
import pytest
from langchain.schema import Document

import services.rag_engine as rag_mod


class FakeRagVectorStore:
    """Stands in for SupabaseVectorStore.similarity_search_with_relevance_scores."""

    def __init__(self, results: list[tuple[Document, float]]):
        self._results = results

    def similarity_search_with_relevance_scores(self, query, **kwargs):
        return self._results


def _doc(source="dmca.txt", law="dmca", content="Section 512 safe harbor text."):
    return Document(page_content=content, metadata={"source": source, "law": law})


@pytest.fixture
def rag_documents():
    return [
        (_doc(content="Highly relevant DMCA takedown text."), 0.91),
        (_doc(source="indian_copyright_act.txt", law="indian_copyright",
              content="Section 51 of the Indian Copyright Act."), 0.55),
        (_doc(content="Irrelevant filler that should be filtered out."), 0.21),
    ]


@pytest.fixture
def fake_rag(rag_documents):
    """Install a fake vector store on the rag_engine module globals."""
    original = rag_mod.rag_vectorstore
    rag_mod.rag_vectorstore = FakeRagVectorStore(rag_documents)
    yield rag_mod.rag_vectorstore
    rag_mod.rag_vectorstore = original


def test_query_rag_returns_dict_shape(fake_rag):
    results = rag_mod.query_rag("pirated sports stream", k=3)
    assert len(results) == 2  # the 0.21-score chunk is filtered out
    for item in results:
        assert set(item.keys()) == {"content", "source", "law", "relevance_score"}
        assert isinstance(item["content"], str) and item["content"]
        assert isinstance(item["source"], str)
        assert isinstance(item["law"], str)
        assert isinstance(item["relevance_score"], float)


def test_query_rag_scores_are_rounded_and_ordered(fake_rag):
    results = rag_mod.query_rag("q", k=3)
    assert results[0]["content"].startswith("Highly relevant")
    assert results[0]["relevance_score"] == 0.91
    assert results[1]["relevance_score"] == 0.55
    assert results[1]["law"] == "indian_copyright"


def test_query_rag_disabled_when_no_vectorstore():
    original = rag_mod.rag_vectorstore
    rag_mod.rag_vectorstore = None
    try:
        assert rag_mod.query_rag("anything", k=3) == []
    finally:
        rag_mod.rag_vectorstore = original
