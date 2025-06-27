from fastapi import FastAPI
from app.routes import pdf_upload
from app.routes import qa

app = FastAPI()
app.include_router(pdf_upload.router)
app.include_router(qa.router)