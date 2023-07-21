from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class SemanticSearch:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.document_id_to_meta = {}

    def split_into_paragraphs(self, doc):
        return doc.split('\n')

    def encode_paragraphs(self, doc_id, paragraphs):
        embeddings = self.model.encode(paragraphs, convert_to_tensor=True)
        if self.index is None:
            self.index = faiss.IndexFlatL2(embeddings.shape[1])

        # Add the embeddings to the Faiss index
        self.index.add(embeddings.cpu().numpy())

        # Store the metadata for each embedding
        for i, paragraph in enumerate(paragraphs):
            self.document_id_to_meta[len(self.document_id_to_meta)] = (doc_id, i, paragraph)

    def load_documents(self, documents):
        for doc_id, doc in documents.items():
            paragraphs = self.split_into_paragraphs(doc)
            self.encode_paragraphs(doc_id, paragraphs)

    def query(self, text, k=5):
        embedding = self.model.encode(text, convert_to_tensor=True)
        distances, indices = self.index.search(embedding.cpu().numpy(), k)
        
        # Fetch the metadata for the matched embeddings
        matches = []
        for distance, index in zip(distances[0], indices[0]):
            doc_id, para_id, paragraph = self.document_id_to_meta[index]
            matches.append((doc_id, para_id, paragraph, distance))

        return matches
