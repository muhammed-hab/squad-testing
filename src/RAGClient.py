import os

import chromadb
from chromadb.utils import embedding_functions


class RAGClient:

    def __init__(self, api_key: str, store_loc: str):
        self.chroma = chromadb.PersistentClient(path=store_loc)
        self.openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name="text-embedding-ada-002"
        )

        self.collection = None

    def train(self, docs: list[str]):
        documents = {str(hash(doc)): doc for doc in docs}
        self.collection = self.chroma.create_collection(
            name="documents",
            embedding_function=self.openai_ef
        )
        self.collection.add(ids=list(documents.keys()), documents=list(documents.values()))

    def query(self, query: str, num_results: int) -> list[str]:
        if self.collection is None:
            self.collection = self.chroma.get_collection(
                name="documents",
                embedding_function=self.openai_ef
            )
        return self.collection.query(query_texts=[query], n_results=num_results)['documents'][0]

if __name__ == "__main__":
    from load_questions import load_questions
    from dotenv import load_dotenv
    load_dotenv()
    questions = load_questions(500)
    rag = RAGClient(os.getenv("OPENAI_API_KEY"), "rag.db")
    # rag.train([question.context for question in questions])

    print(questions[200])
    print(rag.query(questions[200].question, 5))