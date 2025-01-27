from dotenv import load_dotenv
import os

# Tải các biến từ file .env
load_dotenv()

# Lấy các biến môi trường
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
QDRANT_COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME')
QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
NEO4J_PASS = os.getenv('NEO4J_PASS')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_URI = os.getenv('NEO4J_URI')
