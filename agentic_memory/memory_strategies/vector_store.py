import faiss
import numpy as np
from langchain_classic.memory import VectorStoreRetrieverMemory
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.messages import SystemMessage, HumanMessage


class VectorStoreMemoryStrategy:
    """
    Instead of remembering things in order, Nova files every message away
    and later acts like a librarian: when you ask something, she searches
    for just the FEW most relevant memories instead of rereading everything.
    Cost barely grows even after hundreds of turns, because she only ever
    pulls a small handful of relevant memories each time.
    """

    def __init__(self, system_prompt: str, embedder, top_k: int = 3):
        self.system_prompt = system_prompt
        self.embedder = embedder
        self.top_k = top_k

        sample_vector = embedder.embed_query("hello")
        index = faiss.IndexFlatL2(len(sample_vector))
        self.vectorstore = FAISS(
            embedding_function=embedder,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": top_k})
        self.memory = VectorStoreRetrieverMemory(retriever=retriever, memory_key="history")

    def get_messages_for_reply(self, user_text: str):
        retrieved = self.memory.load_memory_variables({"input": user_text})["history"]
        system_content = self.system_prompt
        if retrieved:
            system_content += f"\n\nRelevant memories retrieved for this question:\n{retrieved}"
        return [SystemMessage(content=system_content), HumanMessage(content=user_text)]

    def save(self, user_text: str, reply_text: str):
        self.memory.save_context({"input": user_text}, {"output": reply_text})

    def stored_count(self) -> int:
        return len(self.vectorstore.index_to_docstore_id)

    def all_vectors_and_texts(self):
        """Pulls every stored memory back out, for the 2D map on the page."""
        n = self.vectorstore.index.ntotal
        if n == 0:
            return [], []
        vectors = [self.vectorstore.index.reconstruct(i) for i in range(n)]
        texts = []
        for i in range(n):
            doc_id = self.vectorstore.index_to_docstore_id[i]
            doc = self.vectorstore.docstore.search(doc_id)
            texts.append(getattr(doc, "page_content", str(doc)))
        return np.array(vectors), texts
