import json
import re
from docx import Document

# Hàm trích xuất tham chiếu từ một đoạn văn bản
def extract_references(text):
    # Biểu thức chính quy để bắt các chuỗi "khoản X, khoản Y, ... điều Z" hoặc "điều Z"
    pattern = r"(khoản \d+(?:, khoản \d+)* điều \d+|điều \d+)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    refer = []
    for match in matches:
        refer.append(match)
    return refer

# Hàm phân tích dữ liệu và tạo cấu trúc JSON
def parse_data_to_json(data):
    chapters = []
    current_chapter = None
    current_section = None
    current_article = None
    lines = data.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        # Xử lí chương
        if line.startswith("CHƯƠNG"):
            if current_chapter:
                if current_section: # Thêm mục hiện tại vào chương trước khi chuyển sang chương mới
                    current_chapter["sections"].append(current_section)
                    current_section = None
                chapters.append(current_chapter)            
            current_chapter = {
                "chapter": f"{line} {lines[i+1].strip()}",  # Kết hợp số chương và tiêu đề
                "sections": []
            }
            i += 2 

        # Xử lí Mục
        elif line.startswith("Mục"):
            if current_section:
                if current_article:
                    current_section["articles"].append(current_article)
                    current_article = None
                current_chapter["sections"].append(current_section)
            current_section = {
                "section": f"{line} {lines[i+1].strip()}",  # Kết hợp số mục và tiêu đề
                "articles": []
            }
            i += 2 

        # Xử lí Điều
        elif line.startswith("Điều"):
            if current_section is None:
                current_section = {
                    "section": "",  # Kết hợp số mục và tiêu đề
                    "articles": []
                }
            if current_article:
                current_section["articles"].append(current_article)
            current_article = {
                "article": line,
                "title": line.split('.')[1].strip(),
                "clauses": []
            }
            # text = line.split('.')[1].strip()
            i += 1
            # Kiểm tra xem điều này có câu ngắn trước các khoản không (sử dụng re.match)
            if i < len(lines) and lines[i].strip() and re.match(r"^\D", lines[i].strip()):
                # Lưu câu ngắn để ghép vào khoản đầu tiên
                text = lines[i].strip()
                i += 1
            else:
                text = ""
            flag = False
            
            # Xử lý các khoản
            while i < len(lines) and lines[i].strip() and lines[i].strip()[0].isdigit():
                flag = True
                # Bắt đầu một khoản mới
                clause_number = f"Khoản {lines[i].strip().split('.')[0]}"
                clause_content = lines[i].strip()
                i += 1
                # Xử lý các điểm trong khoản
                while i < len(lines) and lines[i].strip() and re.match(r"^[a-zđ]\)", lines[i].strip()):
                    clause_content += " " + lines[i].strip()
                    i += 1
                # Ghép câu ngắn vào khoản đầu tiên
                if text:
                    clause_content = f"{text} {clause_content}"
                    text = ""  # Đã sử dụng câu ngắn, không cần ghép vào khoản tiếp theo
                refer = extract_references(clause_content)
                current_article["clauses"].append({
                    "clause": clause_number,  # Số khoản
                    "content": clause_content,
                    "refer": refer
                })
            if flag == False:
                refer = extract_references(text)
                current_article["clauses"].append({
                    "clause": "",
                    "content": text,
                    "refer": refer
                })
        else:
            i += 1

    # Thêm các phần còn lại vào cấu trúc
    if current_article:
        current_section["articles"].append(current_article)
    if current_section:
        current_chapter["sections"].append(current_section)
    if current_chapter:
        chapters.append(current_chapter)

    return {"chapters": chapters}

# Đọc file .docx
def read_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

# Đường dẫn đến file .docx
file_path = "data.docx"

# Đọc dữ liệu từ file .docx
data = read_docx(file_path)

# Phân tích dữ liệu và tạo JSON
json_data = parse_data_to_json(data)

# Lưu dữ liệu vào file JSON
with open("legal_data2.json", "w", encoding="utf-8") as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)

print("Dữ liệu đã được lưu vào file legal_data2.json")