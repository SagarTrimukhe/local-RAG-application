# Local RAG Application

A local AI-powered Retrieval-Augmented Generation app. Upload PDFs and ask questions — powered by Ollama, LangChain, ChromaDB, FastAPI, and React.

## Architecture

```
┌────────────┐     ┌────────────┐     ┌────────────┐
│  React UI  │────▶│  FastAPI    │────▶│   Ollama   │
│  (Vite)    │     │  Backend    │     │   (LLM)    │
└────────────┘     └─────┬──────┘     └────────────┘
                         │
                   ┌─────▼──────┐
                   │  ChromaDB  │
                   │ (vectors)  │
                   └────────────┘
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- (For local dev without Docker) Python 3.12+, Node.js 20+, [Ollama](https://ollama.com)

## Quick Start with Docker Compose

```bash
# Start all services (Ollama + Backend + Frontend)
docker compose up --build

# In another terminal, pull the required models into the Ollama container
docker exec -it ollama ollama pull llama3.2
docker exec -it ollama ollama pull nomic-embed-text
```

Open **http://localhost:3000** in your browser.

## Local Development (without Docker)

### 1. Start Ollama and pull models

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs on **http://localhost:8000**. API docs at `/docs`.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on **http://localhost:5173** with API proxy to the backend.

## API Endpoints

| Method | Path      | Description                |
|--------|-----------|----------------------------|
| POST   | `/upload` | Upload a PDF for ingestion |
| POST   | `/ask`    | Ask a question             |
| GET    | `/health` | Health check               |

## Cloud Deployment

The architecture is designed for portability:

- **Backend**: Push the `backend/` Docker image to any container registry (ECR, GCR, ACR) and deploy to ECS, Cloud Run, App Service, K8s, etc. Set `OLLAMA_BASE_URL` to your hosted Ollama endpoint or swap to a cloud LLM provider.
- **Frontend**: Run `npm run build` in `frontend/` and deploy the `dist/` folder to Vercel, Netlify, or Cloudflare Pages. Set `VITE_API_URL` to your deployed backend URL at build time.

## Environment Variables

| Variable          | Default                    | Description                |
|-------------------|----------------------------|----------------------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434`   | Ollama server URL          |
| `LLM_MODEL`       | `llama3.2`                 | Chat model name            |
| `EMBEDDING_MODEL`  | `nomic-embed-text`         | Embedding model name       |
| `CHROMA_PERSIST_DIR` | `./chroma_data`         | ChromaDB storage path      |
| `VITE_API_URL`    | `/api`                     | Backend URL for frontend   |