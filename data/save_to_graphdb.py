from neo4j import GraphDatabase
import json
import os
from dotenv import load_dotenv

load_dotenv()
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASS = os.getenv('NEO4J_PASS')
NEO4J_URI = os.getenv('NEO4J_URI')
AUTH = (NEO4J_USERNAME, NEO4J_PASS)

# Định nghĩa hàm để lưu dữ liệu
def save_to_graphdb(uri, auth, json_file):
    # Kết nối với Neo4j
    driver = GraphDatabase.driver(uri, auth=auth)

    try:
        with driver.session() as session:
            # Đọc dữ liệu từ file JSON
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Lưu từng phần vào Neo4j
            for chapter in data["chapters"]:
                session.write_transaction(create_chapter, chapter)
    finally:
        driver.close()

# Tạo chương
def create_chapter(tx, chapter):
    chapter_query = """
    MERGE (c:Chapter {name: $chapter_name})
    """
    tx.run(chapter_query, chapter_name=chapter["chapter"])

    # Kiểm tra nếu chương có sections
    for section in chapter["sections"]:
        if section["section"]:
            create_section(tx, chapter["chapter"], section)
        else:
            for article in section["articles"]:
                create_article(tx, chapter["chapter"], article, is_direct=True)

# Tạo mục
def create_section(tx, chapter_name, section):
    section_query = """
    MERGE (s:Section {name: $section_name})
    WITH s
    MATCH (c:Chapter {name: $chapter_name})
    MERGE (c)-[:HAS_SECTION]->(s)
    """
    tx.run(section_query, section_name=section["section"], chapter_name=chapter_name)

    for article in section["articles"]:
        create_article(tx, section["section"], article)

# Tạo điều
def create_article(tx, parent_name, article, is_direct=False):
    article_name = f'{article["article"]} {article["title"]}'
    article_query = """
    MERGE (a:Article {name: $article_name})
    """
    tx.run(article_query, article_name=article_name)

    # Liên kết điều với chương hoặc mục
    if is_direct:  # Nếu điều thuộc trực tiếp vào chương
        direct_relationship_query = """
        MATCH (c:Chapter {name: $parent_name}), (a:Article {name: $article_name})
        MERGE (c)-[:HAS_ARTICLE]->(a)
        """
        tx.run(direct_relationship_query, parent_name=parent_name, article_name=article_name)
    else:  # Nếu điều thuộc vào mục
        indirect_relationship_query = """
        MATCH (s:Section {name: $parent_name}), (a:Article {name: $article_name})
        MERGE (s)-[:HAS_ARTICLE]->(a)
        """
        tx.run(indirect_relationship_query, parent_name=parent_name, article_name=article_name)

    # Tạo các khoản trong điều
    for clause in article["clauses"]:
        create_clause(tx, article_name, clause)

# Tạo khoản
def create_clause(tx, article_name, clause):
    clause_query = """
    MERGE (cl:Clause {name: $clause_name, content: $clause_content})
    WITH cl
    MATCH (a:Article {name: $article_name})
    MERGE (a)-[:HAS_CLAUSE]->(cl)
    """
    tx.run(clause_query, clause_name=clause["clause"], clause_content=clause["content"], article_name=article_name)

# Gọi hàm lưu dữ liệu vào Neo4j
save_to_graphdb(NEO4J_URI, AUTH, "data.json")

print("Dữ liệu đã được lưu vào Neo4j!")
