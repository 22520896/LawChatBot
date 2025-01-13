from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class QueryTransform:
    def __init__(self, model="gemini-1.5-flash", temperature=0.3):
        # Prompt
        self.transform_prompt = ChatPromptTemplate.from_template("""
        Bạn là một mô hình phân tích câu hỏi. Nhiệm vụ của bạn là xử lý câu hỏi (hoặc câu khẳng định) của người dùng theo từng bước sau:
        1. Nếu câu hỏi là không hoàn toàn tiếng Việt, trả về Kết quả: Xin lỗi, tôi không hiểu bạn đang nói gì, vui lòng sử dụng tiếng Việt.
        2. Sửa lỗi chính tả, gõ sai, viết tắt cho câu hỏi trong tiếng Việt. Ví dụ: Tôi li hôn đc k? -> Tôi ly hôn được không?, thũ tụt -> thủ tục
        3. NẾU CÂU HỎI CÓ NHIỀU Ý HỎI, tách chúng thành từng câu hỏi riêng biệt. Với mỗi câu hỏi thực hiện các bước tiếp theo.
        4. NẾU CÂU HỎI chứa **SỐ ĐIỀU/SỐ CHƯƠNG cụ thể** và NẾU trong lịch sử trò chuyện gần nhất có chứa:
            + "Vui lòng chọn Điều cụ thể.", thì ý định của câu hỏi là: **Khoản <số Khoản trong lịch sử> Điều <SỐ/SỐ ĐIỀU trong câu hỏi>. Ngược lại ý định là: Điều <SỐ/SỐ ĐIỀU trong câu hỏi> **
            + "Vui lòng chọn Chương cụ thể", thì ý định của câu hỏi là: **Mục <số Mục trong lịch sử> Chương <SỐ/SỐ CHƯƠNG trong câu hỏi>. Ngược lại ý định là: Chương <SỐ/SỐ CHƯƠNG trong câu hỏi> **
        5. **NẾU CÂU HỎI KHÔNG RÕ RÀNG HOẶC CHƯA ĐẦY ĐỦ**, hãy sử dụng lịch sử trò chuyện được cung cấp **CHỈ KHI LỊCH SỬ LIÊN QUAN TRỰC TIẾP ĐẾN CÂU HỎI** để làm rõ ý nghĩa và ngữ cảnh truy vấn của người dùng. **KHÔNG ĐƯỢC THÊM THÔNG TIN KHÔNG LIÊN QUAN VÀO CÂU HỎI**.
        6. Suy ra nội dung chính của câu hỏi (hoặc câu khẳng định) thật đơn giản, rõ ràng và dễ hiểu (dùng các từ ngữ trong luật Hôn nhân và Gia đình nếu có thể), **BỎ QUA ĐẠI TỪ DANH XƯNG NẾU CÓ THỂ**. Ví dụ: Tôi là nữ 16 tuổi thì có lấy chồng được không? -> Nữ 16 tuổi có đủ điều kiện kết hôn không?, Người bị điên có lấy vợ được không? -> Người mất hành vi dân sự có được phép kết hôn không?

        Chỉ cung cấp kết quả **theo định dạng sau** và không thêm bất kỳ văn bản, giải thích hoặc bình luận nào khác:
        Kết quả: <nội dung chính của câu hỏi 1>|<nội dung chính của câu hỏi 2>...

        Lịch sử: {history}
        Câu hỏi gốc: {query}
        """)

        self.model = ChatGoogleGenerativeAI(model=model, temperature=temperature, api_key= "AIzaSyAZ9e7fpVwT_Ao0c2q5IuvZIvuSpN-EXG0")
        self.parser = StrOutputParser()

    def transform(self, raw_query, history):
        # print ("HISTORY: ", history, '\n________________________________________--')
        prompt = self.transform_prompt.format_prompt(query=raw_query, history=history)
        response = self.parser.parse(self.model.invoke(prompt).content)
        lines = response.split("\n")
        result = lines[0].replace("Kết quả:", "").strip()
        return result.split("|") if result else [raw_query]