from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import FastEmbedSparse
from query_transformation import QueryTransform
from route import Router
from retrieval import Retriever
import os
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory


class ChatBot:
    def __init__(self, embedding_model='bkai-foundation-models/vietnamese-bi-encoder', sparse_embedding="Qdrant/BM25"):
        self.embedding_model = HuggingFaceEmbeddings(model_name=embedding_model)
        self.sparse_embedding = FastEmbedSparse(model_name=sparse_embedding)

        genai_api_key = "AIzaSyAZ9e7fpVwT_Ao0c2q5IuvZIvuSpN-EXG0"

        print ("Khởi tạo Query Transform")
        self.query_transform = QueryTransform()

        print ("Khởi tạo Router")
        self.router = Router()

        print ("Khởi tạo Retriever")
        self.retriever = Retriever(self.embedding_model, self.sparse_embedding)

        print ("Khởi tạo LLM")
        self.llm = ChatGoogleGenerativeAI(api_key=genai_api_key, model="gemini-1.5-flash")

        # Sử dụng ConversationBufferMemory để lưu trữ lịch sử hội thoại
        self.memory = ConversationBufferWindowMemory(
                            memory_key="history",
                            input_key="query",
                            return_messages=False,
                            ai_prefix="AI",
                            human_prefix="User",
                            k=2  # Giới hạn số lượng tin nhắn
                        )

        self.prompt_template = """
        Bạn là một chatbot chuyên về Luật Hôn Nhân và Gia Đình Việt Nam với tên "ChatBot hỏi đáp về Luật Hôn Nhân và Gia Đình Việt Nam". Hãy trả lời từng câu hỏi đã được làm rõ (converted_query) dựa trên loại câu hỏi (question_type) và ngữ cảnh (context). Tuân thủ các quy tắc sau:

        - Với `question_type = 1|4|6|8|9`:
            1. Dựa vào ngữ cảnh và câu hỏi đã được làm rõ (converted_query) để trả lời câu hỏi gốc (query). Nếu không có thông tin phù hợp trong ngữ cảnh, trả về "Điều bạn hỏi không nằm trong bộ Luật".
            2. **Chỉ sử dụng thông tin trong ngữ cảnh.** Trả lời một cách **diễn giải chi tiết**, giải thích rõ lý do, cơ sở pháp lý (trong ngữ cảnh, **chỉ ra các điều khoản liên quan nếu có**).
            3. Nếu hỏi về nội dung của Chương/Mục/Điều/Khoản cụ thể thì trả về thông tin y ngữ cảnh, không thêm bớt bất kì thông tin nào.

        - Với `question_type = 2` (smalltalk): Trả lời thân thiện, phù hợp với ngữ cảnh.

        - Với `question_type = 0|3|5|7`: *Trả về ngữ cảnh y như nó được cung cấp, không thêm bớt bất kỳ thông tin nào khác.*

        Mỗi câu hỏi đã được làm rõ (converted_query[i]) tương ứng với `context[i]` và `question_type[i]`. Trả lời lần lượt từng câu hỏi theo các quy tắc trên. **KHÔNG ĐƯỢC sử dụng các cụm từ tương tự như "Dựa vào thông tin được cung cấp", "Dựa vào ngữ cảnh", "không được nêu rõ trong ngữ cảnh".**

        **Cách trình bày câu trả lời:** Tách các thông tin trả lời một cách rõ ràn, không nhắc lại câu hỏi

        Dữ liệu cung cấp:
        - Loại câu hỏi: {question_type}
        - Ngữ cảnh: {context}
        - Câu hỏi gốc: {query}
        - Câu hỏi đã được làm rõ: {converted_query}

        """

        # Prompt template cho LLMChain
        self.prompt = PromptTemplate(
            input_variables=["question_type", "context", "query", "converted_query"],
            template=self.prompt_template,
        )

        # LLMChain kết hợp LLM và Prompt
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt, memory=self.memory)

    def process_query(self, raw_query):
        print ('QUERY GỐC: ', raw_query, '\n---------------------------------------------------------')
        # Bước 1: Biến đổi câu truy vấn dựa trên lịch sử
        converted_queries = self.query_transform.transform(raw_query, self.memory.load_memory_variables({})["history"])
        print ('QUERY ĐÃ TRANSFORM: ', converted_queries, '\n---------------------------------------------------------')
        query_types = []
        # Bước 2: Phân loại loại câu hỏi
        for q in converted_queries:
            query_types.append(self.router.route_query(q))
        print ('LOẠI CỦA QUERY: ', query_types, '\n---------------------------------------------------------')
        # Bước 3: Truy vấn thông tin ngữ cảnh
        context = self.retriever.retrieve(converted_queries, query_types)
        print ('CONTEXT: ', context, '\n---------------------------------------------------------')
        # Bước 4: Tạo câu trả lời bằng LangChain
        response = self.chain.run(question_type=query_types, context=context, query=raw_query, converted_query=converted_queries)
        print ('CÂU TRẢ LỜI: ', response, '\n___________________________________________________________')
        return response
