# AI-Powered RAG Document Q&A System

A Retrieval-Augmented Generation (RAG) application that allows users to ask questions about PDF documents and receive AI-generated answers with source references.

## Features

- PDF text extraction using PyMuPDF
- Text chunking with overlap
- OpenAI text embeddings
- Qdrant vector database
- Semantic search and retrieval
- GPT-4o-mini answer generation
- Source filename and page citation
- FastAPI endpoints for PDF processing and question answering

## Tech Stack

- Python
- FastAPI
- OpenAI API
- Qdrant Cloud
- PyMuPDF
- Uvicorn

## Project Structure

```text
rag-document-qa-system/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── extractor.py
│   ├── chunker.py
│   └── embedding.py
├── documents/
├── ingest.py
├── rag_answer.py
├── search_test.py
├── requirements.txt
└── .gitignore
```

## Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd rag-document-qa-system
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

Never upload your `.env` file or API keys to GitHub.

## Run the API

```bash
python -m uvicorn app.main:app --reload
```

Open API documentation:

http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint       | Description                   |
| ------ | -------------- | ----------------------------- |
| GET    | `/`            | API health check              |
| POST   | `/process-pdf` | Extract and chunk PDF         |
| POST   | `/ask`         | Ask questions about documents |

## Current Project Status

- PDF processing: Implemented
- Embedding generation: Implemented
- Qdrant storage and retrieval: Implemented
- RAG answer generation: Implemented
- FastAPI question endpoint: Implemented
- n8n Cloud integration: In progress

## Author

AI Automation and RAG Project
