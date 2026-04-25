from app.llm_agent.tools.rag.base import Retriever


class InMemoryRetriever(Retriever):
    def __init__(self, documents: list[str] | None = None):
        self.documents = documents or []

    def add_documents(self, docs: list[str]) -> None:
        self.documents.extend(docs)

    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        if not query.strip():
            return self.documents[:top_k]

        query_terms = {term.lower() for term in query.split() if term.strip()}
        scored: list[tuple[int, str]] = []
        for doc in self.documents:
            doc_terms = {term.lower() for term in doc.split()}
            score = len(query_terms.intersection(doc_terms))
            scored.append((score, doc))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [doc for score, doc in scored if score > 0][:top_k]

