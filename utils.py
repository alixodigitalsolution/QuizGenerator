import fitz  # PyMuPDF
import os

def extract_text_from_pdf(pdf_path):
    """
    Extracts all text from a PDF file.
    """
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
