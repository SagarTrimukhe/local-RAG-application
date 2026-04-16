from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.ingest import ingest_pdf
from app.rag import ask_question

app = FastAPI(title="Local RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]


class UploadResponse(BaseModel):
    filename: str
    chunks: int
    message: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        result = ingest_pdf(contents, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return UploadResponse(
        filename=result["filename"],
        chunks=result["chunks"],
        message=f"Successfully processed {result['filename']} into {result['chunks']} chunks.",
    )


@app.post("/ask", response_model=AnswerResponse)
async def ask(req: QuestionRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = ask_question(req.question)
    return AnswerResponse(answer=result["answer"], sources=result["sources"])
