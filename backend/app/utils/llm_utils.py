import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.core.storage import StorageContext
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.text_splitter import TokenTextSplitter
from llama_index.core import Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
Settings.llm = None 

INDEX_DIR = "app/storage/indexes"
TEXT_DIR = "app/storage/texts"

os.makedirs(INDEX_DIR, exist_ok=True)
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

def load_text_from_txt(pdf_id: str) -> str:
    path = os.path.join(TEXT_DIR, f"{pdf_id}.txt")
    if not os.path.exists(path):
        raise FileNotFoundError("Text file not found for this PDF.")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def build_and_save_index(pdf_id: str) -> None:
    text = load_text_from_txt(pdf_id)
    document = Document(text=text, metadata={"pdf_id": pdf_id})

    # Set global text splitter
    Settings.text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=50)

    # Build index from document
    index = VectorStoreIndex.from_documents([document])

    # Save index to disk
    save_path = os.path.join(INDEX_DIR, pdf_id)
    index.storage_context.persist(persist_dir=save_path)
