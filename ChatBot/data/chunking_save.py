import json
from sentence_transformers import SentenceTransformer
from qdrant_client import models
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from typing import List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re

# Khởi tạo SentenceTransformer
model_name = 'bkai-foundation-models/vietnamese-bi-encoder'
model = SentenceTransformer(model_name)


# Load dữ liệu từ file data.json
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Hàm chunking ngữ nghĩa và tạo Document
# class SemanticChunker:
#     def __init__(self, model, breakpoint_percentile_threshold=80):
#         self.model = model
#         self.breakpoint_percentile_threshold = breakpoint_percentile_threshold

#     def split_text(self, text: str) -> List[str]:
#         modified_text = re.sub(r'(\d+)\.', r'\1)', text)
#         # Tách câu
#         sentences = re.split(r'(?<=[.!?])\s+', modified_text)

#         # Tính embedding cho các câu
#         embeddings = self.model.encode(sentences, convert_to_tensor=True).cpu().numpy()

#         # Tính khoảng cách cosine giữa các câu liên tiếp
#         distances = [
#             1 - cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
#             for i in range(len(embeddings) - 1)
#         ]

#         distances.append(0)  # Thêm khoảng cách cho câu cuối (không có câu kế tiếp)

#         # Xác định ngưỡng chia đoạn
#         threshold = np.percentile(distances, self.breakpoint_percentile_threshold)
#         breakpoints = [i for i, dist in enumerate(distances) if dist > threshold]

#         # Tạo các đoạn văn bản
#         chunks = []
#         start = 0
#         for bp in breakpoints:
#             chunks.append(' '.join(sentences[start:bp + 1]))
#             start = bp + 1

#         if start < len(sentences):
#             chunks.append(' '.join(sentences[start:]))

#         return chunks
class SemanticChunker:
    def __init__(self, model, buffer_size=1, breakpoint_percentile_threshold=80):
        self.model = model
        self.buffer_size = buffer_size
        self.breakpoint_percentile_threshold = breakpoint_percentile_threshold

    def split_text(self, text: str) -> List[str]:
        modified_text = re.sub(r'(\d+)\.', r'\1)', text)
        # Tách câu
        # sentences = sent_tokenize(modified_text)
        sentences = re.split(r'(?<=[.!?])\s+', modified_text)

        combined_sentences = [
            ' '.join(sentences[max(i - self.buffer_size, 0): i + self.buffer_size + 1])
            for i in range(len(sentences))
        ]

        # Tính embedding cho các câu
        embeddings = self.model.encode(combined_sentences, convert_to_tensor=True).cpu().numpy()

        # Tính khoảng cách cosine
        distances = [
            1 - cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
            for i in range(len(embeddings) - 1)
        ]

        distances.append(0)  # Thêm khoảng cách cho câu cuối

        # Xác định ngưỡng chia đoạn
        threshold = np.percentile(distances, self.breakpoint_percentile_threshold)
        breakpoints = [i for i, dist in enumerate(distances) if dist > threshold]

        # Tạo các đoạn văn bản
        chunks = []
        start = 0
        for bp in breakpoints:
            chunks.append(' '.join(sentences[start:bp + 1]))
            start = bp + 1

        if start < len(sentences):
            chunks.append(' '.join(sentences[start:]))

        return chunks

# Khởi tạo SemanticChunker
chunker = SemanticChunker(model)

# Hàm xử lý dữ liệu và tạo Document
def chunk_and_embed(data):
    documents = []

    for chapter in data['chapters']:
        print (f"Loading {chapter['chapter']} ...")
        if "sections" in chapter: 
            for section in chapter['sections']:
                for article in section['articles']:
                    chunks = chunker.split_text(article['content'])
                    for chunk in chunks:
                        documents.append(Document(
                            page_content=chunk,
                            metadata={
                                'chapter': chapter['chapter'] + " " + chapter['title'],
                                'section': section['section'] + " " + section['title'],
                                'article': article['article'] + " " + article['title']
                            }
                        ))

        else:
            for article in chapter['articles']:
                chunks = chunker.split_text(article['content'])
                # modified_text = re.sub(r'(\d+)\.', r'\1)', article['content'])
                # chunks = sent_tokenize(modified_text)

                for chunk in chunks:
                    documents.append(Document(
                        page_content=chunk,
                        metadata={
                            'chapter': chapter['chapter'] + " " + chapter['title'],
                            'section': "",
                            'article': article['article'] + " " + article['title']
                        }
                    ))
    return documents

# Tạo các Document từ dữ liệu
documents = chunk_and_embed(data)

print (f'Number of chunks: {len(documents)}')

# Tạo embedding cho các Document bằng SentenceTransformer
embedding_model = HuggingFaceEmbeddings(model_name=model_name)
sparse_embeddings = FastEmbedSparse(model_name="Qdrant/BM25")

# Lưu dữ liệu vào Qdrant
collection_name = "LawData"
vectorstore = QdrantVectorStore.from_documents(
                documents, 
                embedding_model, 
                sparse_embedding=sparse_embeddings,
                retrieval_mode=RetrievalMode.HYBRID,
                url='https://c1e67a53-62f6-4464-b5ed-086b3c298e23.europe-west3-0.gcp.cloud.qdrant.io', 
                api_key='-s29x9W2DpfpvmsR-1bA_CbpKrtp__xVJ2YKUmPgcf6n7MQ95o6fBQ',
                collection_name=collection_name,
                distance=models.Distance.COSINE
            )

print("Dữ liệu đã được lưu vào Qdrant Cloud!")
