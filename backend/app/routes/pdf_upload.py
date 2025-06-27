import os
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST
from typing import Literal
from app.database import SessionLocal
from app.models.document import DocumentMetadata
from app.utils.pdf_utils import extract_text_from_pdf
from app.utils.llm_utils import build_and_save_index

UPLOAD_DIR = "app/storage/pdfs"
MAX_FILE_SIZE_MB = 2

router = APIRouter()

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # Validate content type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed.")

    # Check file size
    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="File too large. Max allowed size is 2 MB.")
    
    # Generate unique filename
    pdf_id = str(uuid.uuid4())
    filename = f"{pdf_id}.pdf"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Save file locally
    with open(file_path, "wb") as f:
        f.write(contents)

    # Extract and save text as .txt
    try:
        extract_text_from_pdf(file_path, pdf_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF.")
    
    # save metadata to neonDB
    db = SessionLocal()
    try:
        doc_meta = DocumentMetadata(
            pdf_id=pdf_id,
            filename=filename,
            index_built=False
        )
        db.add(doc_meta)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save metadata.")
    finally:
        db.close()

    # Build and save index
    try:
        build_and_save_index(pdf_id)
    except Exception as e:
        print("Index error:", e)
        raise HTTPException(status_code=500, detail=f"Failed to build index: {str(e)}")

    return JSONResponse(status_code=200, content={
        "message": "PDF uploaded successfully",
        "pdf_id": pdf_id,
        "filename": filename
    })
