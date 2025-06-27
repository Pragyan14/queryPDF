from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime
from ..database import Base

class DocumentMetadata(Base):
    __tablename__ = "documents"

    pdf_id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    index_built = Column(Boolean, default=False)
