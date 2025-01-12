from semantic_router import Route
from semantic_router.encoders import HuggingFaceEncoder
from semantic_router.layer import RouteLayer
import re


class Router:
    def __init__(self, model_name="dangvantuan/vietnamese-embedding"):
        self.encoder = HuggingFaceEncoder(model_name=model_name)
        self.routes = self.initialize_routes()
        self.rl = RouteLayer(encoder=self.encoder, routes=self.routes)

    def initialize_routes(self):
        # Route cho câu hỏi liên quan đến hôn nhân và gia đình
        marriage_and_family = Route(
            name="1",
            score_thresold=0.64,
            utterances=[
                "quy định về kết hôn như thế nào?",
                "ly hôn có cần sự đồng ý của cả hai không?",
                "quyền nuôi con sau khi ly hôn thuộc về ai?",
                "phân chia tài sản khi ly hôn thế nào?",
                "điều kiện để nhận con nuôi là gì?",
                "kết hôn có cần đăng ký không?",
                "ngoại tình có vi phạm pháp luật không?",
                "người không nuôi con có quyền thăm con sau ly hôn không?",
                "kết hôn với người nước ngoài cần những giấy tờ gì?",
                "tảo hôn là gì?",
                "ông bà có quyền nuôi cháu sau khi cha mẹ ly hôn không?",
            ],
        )

        # Route cho smalltalk
        smalltalk = Route(
            name="2",
            score_thresold=0.34,
            utterances=[
                "chào bạn!",
                "hôm nay trời đẹp nhỉ?",
                "bạn có thể giúp tôi không?",
                "bạn tên là gì?",
                "bạn làm việc ở đâu?",
                "bạn khỏe không?",
                "rất vui được gặp bạn!",
                "bạn thông minh lắm đấy!",
                "bạn có sở thích gì không?",
                "cảm ơn bạn.",
                "tạm biệt.",
                "Xin chào",
                "Bạn thú vị đó!",
                "Có gì vui không, kể cho tôi nghe với?",
                "Giúp tôi tí được không?",
                "Có kế hoạch gì hay không bạn?",
                "Bạn có thể làm gì",
            ],
        )

        # Route cho câu hỏi không liên quan
        unrelated = Route(
            name="3",
            score_thresold=0.9,
            utterances=[
                "Những món ăn nào phổ biến nhất ở Ấn Độ?",
                "Tại sao con người cần có mục tiêu?",
                "Tự do cá nhân có quan trọng không?",
                "Cách chăm sóc cây cảnh trong nhà?",
                "AI có thể thay đổi cuộc sống của con người ra sao?",
                "Blockchain là gì và nó hoạt động như thế nào?",
                "Ai là cầu thủ ghi nhiều bàn thắng nhất mọi thời đại?",
                "Tại sao Kim tự tháp được coi là kỳ quan?",
                "Cuộc cách mạng công nghiệp diễn ra khi nào?",
                "Ý nghĩa cuộc sống?",
                "Nước là gì?",
                "Con người có phải loài thông minh nhất?"
            ],
        )
        return [marriage_and_family, smalltalk, unrelated]

    def route_query(self, query):
        """
        Xác định loại câu hỏi dựa trên nội dung query.
        """
        query_ = query.strip().lower()  # Chuẩn hóa query

        if query_ == "không hiểu":
            return 0

        patterns = {
            4: r"\bkhoản\s+\d+\b.*\bđiều\s+\d+\b",  # Có khoản và điều cụ thể
            5: r"\bkhoản\s+\d+\b(?!.*\bđiều\b)",    # Chỉ có khoản cụ thể, không có điều
            6: r"\bmục\s+\d+\b.*\bchương\s+([IVXLCDMivxlcdm]+|\d+)\b",  # Có mục và chương cụ thể (số La Mã hoặc số thường)
            7: r"\bmục\s+\d+\b(?!.*\bchương\b)",    # Chỉ có mục cụ thể, không có chương
            8: r"\bđiều\s+\d+\b",                   # Chỉ có điều cụ thể
            9: r"\bchương\s+([IVXLCDMivxlcdm]+|\d+)\b"  # Chỉ có chương cụ thể (số La Mã hoặc số thường)
        }

        # Kiểm tra từng mẫu regex
        for query_type, pattern in patterns.items():
            if re.search(pattern, query_, re.IGNORECASE):
                return query_type

        query_type = self.rl(query).name
        return int(query_type) if query_type else 3