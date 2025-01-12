from fastapi import FastAPI
from pydantic import BaseModel
from chatbot import ChatBot
import warnings
from fastapi.middleware.cors import CORSMiddleware
# Tắt các cảnh báo
warnings.filterwarnings("ignore")

# Khởi tạo ứng dụng FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Cho phép kết nối từ frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Khởi tạo chatbot
chatbot = ChatBot()

# Định nghĩa schema cho dữ liệu đầu vào
class QueryRequest(BaseModel):
    query: str

# Endpoint để khởi tạo lại chatbot
@app.post("/newchat/")
async def new_chat():
    global chatbot
    chatbot = ChatBot()  # Khởi tạo lại chatbot mới
    return {"message": "ChatBot đã được khởi tạo lại."}

# Endpoint để xử lý câu hỏi
@app.post("/process_query/")
async def process_query(request: QueryRequest):
    global chatbot
    
    raw_query = request.query  # Lấy query từ người dùng
    # Xử lý truy vấn bằng chatbot
    response = chatbot.process_query(raw_query)
    # Trả về câu trả lời từ chatbot
    return {"response": response}
