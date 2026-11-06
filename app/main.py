import hashlib
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel


from app.extractor import extract_pdf
from app.chunker import chunk_text
from rag_answer import ask_question

from app.vector_store import (
    store_chunks,
    list_documents,
    delete_document,
    is_duplicate_file
)
app = FastAPI(
    title="RAG Document Processing API",
    version="1.0.0"
)


class QuestionRequest(BaseModel):
    question: str
    document_id: str | None = None

@app.get("/")
def home():
    return {
        "message": "RAG Document Processing API is running"
    }
@app.get("/documents")
def get_documents():

    try:
        documents = list_documents()

        return {
            "total_documents": len(documents),
            "documents": documents
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve documents: {str(error)}"
        )
@app.delete("/documents/{document_id}")
def remove_document(document_id: str):

    try:
        deleted = delete_document(document_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        return {
            "message": "Document deleted successfully",
            "document_id": document_id
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(error)}"
        )


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

    file_hash = hashlib.sha256(pdf_bytes).hexdigest()

    if is_duplicate_file(file_hash):
        raise HTTPException(
            status_code=409,
            detail="This PDF has already been uploaded."
        )

    try:
        pages = extract_pdf(pdf_bytes)

        if not pages:
            raise HTTPException(
                status_code=422,
                detail="No extractable text found in PDF"
            )

        chunks = chunk_text(pages)

        storage_result = store_chunks(
            chunks,
            file.filename or "uploaded.pdf",
            file_hash
        )

        return {
            "filename": file.filename,
            "total_pages": len(pages),
            "total_chunks": len(chunks),
            "document_id": storage_result["document_id"],
            "total_chunks_saved": storage_result["total_chunks_saved"],
            "message": "PDF successfully processed and stored in Qdrant!"
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"PDF processing failed: {str(error)}"
        )

        return {
    "filename": file.filename,
    "total_pages": len(pages),
    "total_chunks": len(chunks),
    "document_id": storage_result["document_id"],
    "total_chunks_saved": storage_result["total_chunks_saved"],
    "message": "PDF successfully processed and stored in Qdrant!"
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
        answer = ask_question(
            request.question,
            document_id=request.document_id
        )

        return {
            "question": request.question,
            "document_id": request.document_id,
            "answer": answer
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Question answering failed: {str(error)}"
        )
 