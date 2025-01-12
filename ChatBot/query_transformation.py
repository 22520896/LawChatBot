from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
class QueryTransform:
    def __init__(self, model="gemini-1.5-flash", temperature=0.3):
        load_dotenv()
        genai_api_key = os.getenv('GOOGLE_API_KEY')

        # Prompt
        self.transform_prompt = ChatPromptTemplate.from_template("""
        Bạn là một mô hình phân tích câu hỏi. Nhiệm vụ của bạn là xử lý câu hỏi (hoặc câu khẳng định) của người dùng theo từng bước sau:
        1. Nếu câu hỏi là ngôn ngữ khác tiếng Việt, trả về Kết quả: Xin lỗi, tôi không hiểu bạn đang nói gì, vui lòng sử dụng tiếng Việt.
        2. Sửa lỗi chính tả, gõ sai, viết tắt cho câu hỏi trong tiếng Việt. Ví dụ: Tôi li hôn đc k? -> Tôi ly hôn được không?, thũ tụt -> thủ tục
        3. NẾU CÂU HỎI CÓ NHIỀU Ý HỎI, tách chúng thành từng câu hỏi riêng biệt. Với mỗi câu hỏi thực hiện các bước tiếp theo.
        4. NẾU CÂU HỎI chứa SỐ ĐIỀU/SỐ CHƯƠNG cụ thể và trong lịch sử trò chuyện có chứa:
            + "Vui lòng chọn Điều cụ thể.", thì ý định của câu hỏi là: Khoản <số Khoản trong lịch sử> Điều <SỐ/SỐ ĐIỀU trong câu hỏi>. Ngược lại ý định là: Điều <SỐ/SỐ ĐIỀU trong câu hỏi>
            + "Vui lòng chọn Chương cụ thể", thì ý định của câu hỏi là: Mục <số Mục trong lịch sử> Chương <SỐ/SỐ CHƯƠNG trong câu hỏi>. Ngược lại ý định là: Chương <SỐ/SỐ CHƯƠNG trong câu hỏi>
        5. **NẾU CÂU HỎI KHÔNG RÕ RÀNG HOẶC CHƯA ĐẦY ĐỦ**, hãy sử dụng lịch sử trò chuyện được cung cấp **CHỈ KHI NÓ LIÊN QUAN TRỰC TIẾP ĐẾN CÂU HỎI** để làm rõ ý nghĩa và ngữ cảnh truy vấn của người dùng. **BỎ QUA THÔNG TIN KHÔNG LIÊN QUAN**.
        6. Suy ra nội dung chính của câu hỏi (hoặc câu khẳng định) thật đơn giản, rõ ràng và dễ hiểu (dùng các từ ngữ trong luật Hôn nhân và Gia đình nếu có thể), **BỎ QUA ĐẠI TỪ DANH XƯNG NẾU CÓ THỂ**. Ví dụ: Tôi là nữ 16 tuổi thì có lấy chồng được không? -> Nữ 16 tuổi có đủ điều kiện kết hôn không?, Người bị điên có lấy vợ được không? -> Người mất hành vi dân sự có được phép kết hôn không?

        Chỉ cung cấp kết quả **theo định dạng sau** và không thêm bất kỳ văn bản, giải thích hoặc bình luận nào khác:
        Kết quả: <nội dung chính của câu hỏi 1>|<nội dung chính của câu hỏi 2>...

        Lịch sử: {history}
        Câu hỏi gốc: {query}
        """)

        self.model = ChatGoogleGenerativeAI(api_key=genai_api_key, model=model, temperature=temperature)
        self.parser = StrOutputParser()

    def transform(self, raw_query, history):
        prompt = self.transform_prompt.format_prompt(query=raw_query, history=history)
        response = self.parser.parse(self.model.invoke(prompt).content)
        lines = response.split("\n")
        result = lines[0].replace("Kết quả:", "").strip()
        result = result.split("|")
        return result