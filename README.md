Chatbot hỏi đáp về Luật Hôn nhân và Gia đình Việt Nam 
📝 Mô tả chatbot
Chatbot hỏi đáp về Luật Hôn nhân và Gia đình Việt Nam là một hệ thống hỗ trợ tự động sử dụng trí tuệ nhân tạo, cung cấp thông tin và giải đáp các câu hỏi liên quan đến Luật Hôn nhân và Gia đình tại Việt Nam.

⚙️ Tính năng chính
+ Khả năng trả lời các câu hỏi liên quan đến luật Hôn nhân và Gia đình Việt Nam một cách nhanh chóng và chính xác
+ Hiển thị các điều luật cụ thể khi người dùng yêu cầu: Thay vì phải tìm kiếm trong toàn bộ văn bản pháp luật dài dòng, người dùng chỉ cần đặt câu hỏi và chatbot sẽ truy xuất chính xác điều luật phù hợp.
+ Tích hợp khả năng trò chuyện xã giao, giúp người dùng cảm thấy thoải mái khi tìm hiểu về pháp luật.
🛠️ Công nghệ sử dụng
Ngôn ngữ lập trình: Python
Thư viện:
sentence_transformers: Thư viện sử dụng các mô hình Sentence Transformers, dùng để tạo embeddings từ văn bản.
Google API: Hiểu và phân tích câu hỏi ngôn ngữ tự nhiên.
Reactjs/FastAPI: Xây dựng giao diện API.
🚀 Cách sử dụng
1. Cài đặt yêu cầu
Cài đặt các thư viện cần thiết bằng cách sử dụng pip:

pip install -r requirements.txt
2. Chạy ứng dụng
Khởi động ứng dụng bằng lệnh:
cd ChatBot
uvicorn app:app --reload
cd FrontEnd
npm run dev 
3. Tương tác với chatbot
Truy cập giao diện web tại http://localhost:5173.
Nhập câu hỏi của bạn vào ô chat và nhận câu trả lời từ chatbot.
