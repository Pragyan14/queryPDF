import fitz  # PyMuPDF
import os

TEXT_DIR = "app/storage/texts"
os.makedirs(TEXT_DIR, exist_ok=True)

def extract_text_from_pdf(file_path: str, pdf_id: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    # Save extracted text to .txt file
    text_path = os.path.join(TEXT_DIR, f"{pdf_id}.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text)

    return text
