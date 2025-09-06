import io
import os
from PyPDF2 import PdfReader
from docx import Document
import uuid

def parse_pdf(file):
    reader = PdfReader(io.BytesIO(file.getvalue()))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def parse_docx(file):
    doc = Document(io.BytesIO(file.getvalue()))
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def parse_text_file(file):
    return file.getvalue().decode('utf-8')

def parse_document(file):
    file_type = file.type
    if "pdf" in file_type:
        return parse_pdf(file)
    elif "word" in file_type:
        return parse_docx(file)
    elif "text" in file_type:
        return parse_text_file(file)
    else:
        return None

def save_uploaded_file(uploaded_file):
    try:
        os.makedirs("resumes", exist_ok=True)
        unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
        file_path = os.path.join("resumes", unique_filename)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        print(f"Error saving file: {e}")
        return None