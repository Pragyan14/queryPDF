from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import pdf_upload
from app.routes import qa

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 frontend dev URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(pdf_upload.router)
app.include_router(qa.router)