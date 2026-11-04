
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.extractor import extract_pdf
from app.chunker import chunk_text
from rag_answer import ask_question

app = FastAPI(
    title="RAG Document Processing API",
    version="1.0.0"
)


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "RAG Document Processing API is running"
    }


@app.post("/process-pdf")
async def process_pdf(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    pdf_bytes = await file.read()

    if not pdf_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty"
        )

    try:
        pages = extract_pdf(pdf_bytes)

        if not pages:
            raise HTTPException(
                status_code=422,
                detail="No extractable text found in PDF"
            )

        chunks = chunk_text(pages)

        return {
            "filename": file.filename,
            "total_pages": len(pages),
            "total_chunks": len(chunks),
            "chunks": chunks
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"PDF processing failed: {str(error)}"
        )


@app.post("/ask")
def ask(request: QuestionRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        answer = ask_question(request.question)

        return {
            "question": request.question,
            "answer": answer
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Question answering failed: {str(error)}"
        )
 