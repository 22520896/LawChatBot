import os
from dotenv import load_dotenv
from langchain_qdrant import  RetrievalMode
from langchain_qdrant import QdrantVectorStore
from qdrant_client import models
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
from neo4j import GraphDatabase
import re
import roman

class Retriever:
    def __init__(self, embedding_model, sparse_embedding, rerank_model="itdainb/PhoRanker"):
        # Tải các biến môi trường từ file .env
        load_dotenv()
        collection_name = "LAW"
        url ="https://c1e67a53-62f6-4464-b5ed-086b3c298e23.europe-west3-0.gcp.cloud.qdrant.io"
        api_key = "-s29x9W2DpfpvmsR-1bA_CbpKrtp__xVJ2YKUmPgcf6n7MQ95o6fBQ"
        uri = "neo4j+s://615fc5a0.databases.neo4j.io"
        auth = ("neo4j", "na-qdn-vkgFz_gxp3wchu_w-KLVafhGNebbm1X20An0")

        # Khởi tạo kho lưu trữ vector
        self.vector_store = QdrantVectorStore.from_existing_collection(
            embedding=embedding_model,
            collection_name=collection_name,
            url=url,
            api_key=api_key,
            sparse_embedding=sparse_embedding,
            retrieval_mode=RetrievalMode.HYBRID,
        )

        self.retriever = self.vector_store.as_retriever()
        self.tokenizer = AutoTokenizer.from_pretrained(rerank_model)
        self.rerank_model = AutoModelForSequenceClassification.from_pretrained(rerank_model)
        self.driver = GraphDatabase.driver(uri, auth=auth)

        self.methods = {
            0: self.unknown,                # Ngôn ngữ khác
            1: self.marriage_and_family,    # Tổng quát
            2: self.smalltalk,              # Smalltalk
            3: self.unrelated,              # Không liên quan
            4: self.khoan_with_dieu,        # Khoản có Điều
            5: self.khoan_no_dieu,          # Khoản không có
            6: self.muc_with_chuong,        # Mục có Chương
            7: self.muc_no_chuong,          # Mục không có Chương
            8: self.dieu_only,              # Chỉ có Điều
            9: self.chuong_only,            # Chỉ có Chương
        }

    def rerank(self, query, documents):
        # Tokenize query và documents
        inputs = self.tokenizer([query] * len(documents), documents, return_tensors="pt", padding=True, truncation=True)

        # Tính điểm số
        with torch.no_grad():
            outputs = self.rerank_model(**inputs)
            scores = outputs.logits.squeeze().tolist()

        indexed_documents = list(zip(range(len(documents)), scores))
        indexed_documents.sort(key=lambda x: x[1], reverse=True)
        ranked_indices = [i for i, _ in indexed_documents]

        return ranked_indices

    def unknown(self, query):
        return query

    def marriage_and_family(self, query, top_k=10, top_n=5, rerank=False):

        results = self.retriever.get_relevant_documents(query, k=top_k)

        if rerank:
            docs = [doc.page_content for doc in results]
            docs = self.rerank(query, docs)
            results = [results[i] for i in docs]

        res = {}
        refers = set()
        for doc in results[:top_n]:
            article = doc.metadata['article']
            if article == "Điều 3":
                if article not in res:
                    res[article] = {'title': doc.metadata['art_title'],
                                    'content': set([doc.page_content])}
                else: res[article]['content'].add(doc.page_content)

            elif article not in res:
                res[article] = {'title': doc.metadata['art_title']}

                filter_condition = models.Filter(must=[models.FieldCondition(
                                                        key="metadata.article",  # Trường metadata cần lọc
                                                        match=models.MatchValue(value=article),
                                                    )])
                temp = self.retriever.get_relevant_documents(query="", filter=filter_condition)
                res[article]['content'] = set([d.page_content for d in temp])
                for art in temp:
                    if art.metadata['refer']: refers.update(art.metadata['refer'])

        for ref in refers:
            match_ = re.match(r"(?:Khoản\s*(\d+)\s*)?điều\s*(\d+)", ref, re.IGNORECASE)
            refer_clause = match_.group(1)
            refer_article = f"Điều {match_.group(2)}"
            if refer_article not in res:
                res[refer_article] = {'title': None, 'content': set()}
            filter_condition2 = models.Filter(must=[models.FieldCondition(
                                                        key="metadata.article",
                                                        match=models.MatchValue(
                                                        value=refer_article))] )
            if refer_clause:
              filter_condition2.must.append(models.FieldCondition(
                                                key="metadata.clause",
                                                match=models.MatchValue(value=f"Khoản {refer_clause}")))
            temp2 = self.retriever.get_relevant_documents(query="", filter=filter_condition2)
            res[refer_article]['content'].update([d.page_content for d in temp2])
            res[refer_article]['title'] = temp2[0].metadata['art_title']
        print ('res: ', res)
        context = ""
        for key, value in res.items():
            context += f"{key}: {value['title']}\n"
            for item in value["content"]:
                context += f"{item}\n"
            context += "\n"
        return context

    def smalltalk(self, query):
        return query

    def unrelated(self, query):
        return "Xin lỗi, câu hỏi này không phải lĩnh vực của tôi."

    def muc_no_chuong(self, query):
        return "Vui lòng chọn Chương cụ thể."

    def muc_with_chuong(self, query):
        # Tìm mục và chương từ câu truy vấn
        match = re.search(r"mục\s+(\d+).*chương\s+(\w+)", query, re.IGNORECASE)

        section = int(match.group(1))
        chapter = match.group(2).upper()

        # Xử lý chương
        if chapter.isdigit():
            chapter_number = int(chapter)
            chapter_roman = roman.toRoman(chapter_number)
        else:
            try:
                chapter_number = roman.fromRoman(chapter)
                chapter_roman = chapter
            except roman.InvalidRomanNumeralError:
                return f"'{chapter}' không phải là số hoặc số La Mã hợp lệ."

        if chapter_number < 1 or chapter_number > 10:
            return f"Luật Hôn nhân và Gia Đình Việt Nam không có Chương {chapter}."

        # Truy vấn cơ sở dữ liệu
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (ch:Chapter)-[:HAS_SECTION]->(sec:Section)-[:HAS_ARTICLE]->(art:Article)
                WHERE ch.name =~ $chapter_pattern AND sec.name =~ $section_pattern
                RETURN ch.name AS chapter_name, sec.name AS section_name, art.name AS article_name
                """,
                chapter_pattern=f"^CHƯƠNG {chapter_roman}(\\s|$).*",
                section_pattern=f"^Mục {section}(\\s|$).*"
            )

            # Xử lý kết quả
            records = result.data()
            if not records:
                return f"Chương {chapter} không có mục {section}."

            # Xây dựng nội dung trả về
            context = f"{records[0]['chapter_name']} - {records[0]['section_name']}:"
            for record in records:
                context += f"\n    - {record['article_name']}"

            return context

    def khoan_no_dieu(self, query):
        return "Vui lòng chọn Điều cụ thể."

    def khoan_with_dieu(self, query): # Khoản có Điều
        match = re.search(r"khoản\s+(\d+)\s+điều\s+(\d+)", query, re.IGNORECASE)
        clause, article = match.group(1), match.group(2)
        if int(article) < 1 or int(article) > 133:
            return f'Luật Hôn nhân và Gia Đình Việt Nam không có Điều {article}'

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (a:Article)-[:HAS_CLAUSE]->(c:Clause)
                WHERE a.name =~ $article_number AND c.name = $clause_number
                RETURN a.name AS article_name, c.content AS clause_content
                """,
                article_number=f"^Điều {article}(\\s|$).*",
                clause_number=f"Khoản {clause}",
            )
            record = result.single()
            if record:
                context = f"{record['article_name']}:\n{record['clause_content']}"
                return context
            return f"Điều {article} không có Khoản {clause}."


    def dieu_only(self, query):
        # Tìm số điều từ query
        match = re.search(r"điều\s+(\d+)", query, re.IGNORECASE)

        article = match.group(1)
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (a:Article)-[:HAS_CLAUSE]->(c:Clause)
                WHERE a.name =~ $article_number
                RETURN a.name AS article_name, c.content AS clause_content
                """,
                article_number=f"^Điều {article}(\\s|$).*",
            )

            # Xử lý kết quả truy vấn
            records = result.data()
            if not records:
                return f'Luật Hôn nhân và Gia Đình Việt Nam không có Điều {article}'

            # Tạo nội dung trả về
            context = f"{records[0]['article_name']}:"
            for record in records:
                context += f"\n{record['clause_content']}"
            return context


    def chuong_only(self, query):
        # Tìm số chương từ câu truy vấn
        match = re.search(r"chương\s+(\w+)", query, re.IGNORECASE)
        chapter = match.group(1).upper()
        if chapter.isdigit():
            chapter_number = int(chapter)
            chapter_roman = roman.toRoman(chapter_number)
        else:
            try:
                chapter_number = roman.fromRoman(chapter)
                chapter_roman = chapter
            except roman.InvalidRomanNumeralError:
                return f"'{chapter}' không phải là số hoặc số La Mã hợp lệ."

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (ch:Chapter)
                WHERE ch.name =~ $chapter_pattern
                OPTIONAL MATCH (ch)-[:HAS_SECTION]->(sec:Section)-[:HAS_ARTICLE]->(art:Article)
                OPTIONAL MATCH (ch)-[:HAS_ARTICLE]->(art_direct:Article)
                RETURN ch.name AS chapter_name,
                      sec.name AS section_name,
                      art.name AS article_name,
                      art_direct.name AS direct_article_name
                """,
                chapter_pattern=f"^CHƯƠNG {chapter_roman}(\\s|$).*"
            )

            # Xử lý kết quả
            records = result.data()
            if not records:
                return f"Không tìm thấy dữ liệu cho Chương {chapter}."

            # Xây dựng nội dung trả về
            context = f"{records[0]['chapter_name']}:"
            sections = {}
            direct_articles = []

            for record in records:
                if record['section_name']:
                    section_name = record['section_name']
                    article_name = record['article_name']
                    if section_name not in sections:
                        sections[section_name] = []
                    if article_name:
                        sections[section_name].append(article_name)
                if record['direct_article_name']:
                    direct_articles.append(record['direct_article_name'])

            # Ghi các section và article của chúng
            for section, articles in sections.items():
                context += f"\n{section}:"
                for article in articles:
                    context += f"\n    - {article}"

            # Ghi các article trực tiếp của chương
            if direct_articles:
                for article in direct_articles:
                    context += f"\n    - {article}"

            return context

    def retrieve(self, queries, types):
        context = ""
        for q, t in zip(queries, types):
            context += self.methods[t](q) + "\n----------------"

        return context