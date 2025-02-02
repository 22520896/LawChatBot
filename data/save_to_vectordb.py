import json
from qdrant_client import models
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import os
from dotenv import load_dotenv

def save_to_vectordb(data):
    documents = []
    for chapter in data['chapters']:
        print (f"Loading {chapter['chapter']} ...")
        for section in chapter['sections']:
            for article in section['articles']:
                for clause in article['clauses']:
                    chunk = clause['content']
                    if clause['clause'] == '' or clause['clause'] == 'Khoản 1':
                        chunk = article['title'] + ". " + clause['content']                                
                    documents.append(Document(
                        page_content=chunk,
                        metadata={
                            'chapter': chapter['chapter'],
                            'section': section['section'],
                            'article': article['article'],
                            'art_title': article['title'],
                            'clause': clause['clause'],
                            'refer': clause['refer']
                        }
                    ))

    return documents

with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Tạo các Document từ dữ liệu
documents = save_to_vectordb(data)

# Tạo embedding cho các Document bằng SentenceTransformer
model_name = 'bkai-foundation-models/vietnamese-bi-encoder'
embedding_model = HuggingFaceEmbeddings(model_name=model_name)
sparse_embeddings = FastEmbedSparse(model_name="Qdrant/BM25")

load_dotenv('../env')
QDRANT_COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME')
QDRANT_URL= os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')

# Lưu dữ liệu vào Qdrant'
vectorstore = QdrantVectorStore.from_documents(
                documents, 
                embedding_model, 
                sparse_embedding=sparse_embeddings,
                retrieval_mode=RetrievalMode.HYBRID,
                url=QDRANT_URL, 
                api_key=QDRANT_API_KEY,
                collection_name=QDRANT_COLLECTION_NAME,
                distance=models.Distance.COSINE
            )

print("Dữ liệu đã được lưu vào Qdrant Cloud!")
