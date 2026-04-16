import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from app.config import (
    OLLAMA_BASE_URL,
    EMBEDDING_MODEL,
    CHROMA_PERSIST_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def get_embeddings():
    return OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )


def get_vector_store(collection_name: str = "pdf_docs"):
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_PERSIST_DIR,
    )


def ingest_pdf(file_bytes: bytes, filename: str) -> dict:
    text = extract_text_from_pdf(file_bytes)
    if not text.strip():
        raise ValueError("Could not extract text from the PDF.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.create_documents(
        texts=[text],
        metadatas=[{"source": filename}],
    )

    store = get_vector_store()
    store.add_documents(chunks)

    return {"filename": filename, "chunks": len(chunks)}
