# AI Document Q&A System (RAG)

A Python-based Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and ask questions based on their content. The system extracts text, generates embeddings, stores document vectors in Qdrant, and uses Gemini AI to generate context-aware answers.

## Features

- Upload PDF documents through FastAPI
- Extract text and page information from PDF files
- Split extracted text into manageable chunks
- Generate text embeddings using Gemini
- Store and retrieve document vectors using Qdrant
- Perform semantic search on uploaded documents
- Retrieve information using document IDs
- Generate AI-powered answers based on retrieved context
- Detect duplicate PDF uploads
- Return relevant source information and page references

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| AI Model | Google Gemini |
| Embedding Model | gemini-embedding-001 |
| Embedding Dimension | 768 |
| Vector Database | Qdrant |
| PDF Processing | Python PDF extraction libraries |
| API Documentation | Swagger UI |

## Project Architecture

1. User uploads a PDF document.
2. FastAPI receives and processes the file.
3. Text is extracted from the PDF.
4. Extracted text is divided into chunks.
5. Gemini generates embeddings for each chunk.
6. Embeddings and metadata are stored in Qdrant.
7. User submits a question.
8. The system retrieves relevant document chunks through semantic search.
9. Gemini generates an answer using the retrieved context.

## Project Structure

```text
rag-document-qa-system/
│
├── app/
│   ├── __init__.py
│   ├── chunker.py
│   ├── embedding.py
│   ├── extractor.py
│   ├── main.py
│   └── vector_store.py
│
├── documents/
│   ├── training_institute_handbook.pdf
│   └── advanced_python_handbook.pdf
│
├── ingest.py
├── rag_answer.py
├── search_test.py
├── test_embedding.py
├── test_qdrant.py
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/nadiya758/rag-document-qa-system.git
cd rag-document-qa-system
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

Windows:

```bash
venv\Scripts\activate
```

Linux / macOS:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

Use your own API credentials. Never upload `.env` or expose API keys publicly.

## Run the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Application information |
| `/process-pdf` | POST | Upload and process a PDF |
| `/docs` | GET | Interactive API documentation |

## Current Project Status

The project currently supports:

- PDF upload and processing
- Text extraction and chunking
- Gemini embedding generation
- Qdrant vector storage
- Document ID-based retrieval
- Duplicate PDF detection
- Semantic search and AI-powered question answering

Further improvements are planned for multi-document testing, fallback responses, validation, security, and deployment.

## Future Improvements

- n8n workflow integration
- Improved error handling and validation
- Stronger document-level access control
- Deployment and production configuration
- More comprehensive testing

## Author

**Nadia Jahan**

Diploma in Computer Technology Student  
Aspiring AI Automation & RAG Developer

GitHub: https://github.com/nadiya758

Project Repository: https://github.com/nadiya758/rag-document-qa-system
