import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


# Load .env variables
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Set llama-index to only use embeddings, not LLM
Settings.llm = None
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Init InferenceClient with chat support
client = InferenceClient(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    token=HF_TOKEN,
)

router = APIRouter()
INDEX_DIR = "app/storage/indexes"

class QuestionRequest(BaseModel):
    pdf_id: str
    question: str

@router.post("/ask-question")
async def ask_question(payload: QuestionRequest):
    pdf_id = payload.pdf_id.strip()
    question = payload.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    index_path = os.path.join(INDEX_DIR, pdf_id)
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Index not found for this PDF.")

    try:
        # Load vector index for context retrieval
        storage_context = StorageContext.from_defaults(persist_dir=index_path)
        index = load_index_from_storage(storage_context)
        query_engine = index.as_query_engine(similarity_top_k=2)
        context = str(query_engine.query(question))

        # Use chat API for response generation
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a document QA assistant. Answer the user's question strictly using the content provided in the context. If the question is unclear or the answer is not present in the context, respond with 'I don’t know'."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
            ],
            max_tokens=512,
            temperature=0.7
        )

        return {
            "pdf_id": pdf_id,
            "question": question,
            "answer": response.choices[0].message.content.strip(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")
