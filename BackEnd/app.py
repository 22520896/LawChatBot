from fastapi import FastAPI
from pydantic import BaseModel
from chatbot import ChatBot
import warnings
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import time
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
@app.get("/newchat/")
async def new_chat():
    global chatbot
    chatbot = ChatBot()  # Khởi tạo lại chatbot mới
    return {"message": "ChatBot đã được khởi tạo lại."}

# Endpoint để xử lý câu hỏi
@app.post("/process_query_stream/")
async def process_query_stream(request: QueryRequest):
    global chatbot
    try:
        raw_query = request.query
        # Sử dụng generator để trả về từng phần của câu trả lời
        def generate():
            for chunk in chatbot.process_query_stream(raw_query):
                yield chunk
        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))