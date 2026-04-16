from langchain_ollama import ChatOllama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from app.config import OLLAMA_BASE_URL, LLM_MODEL
from app.ingest import get_vector_store

_PROMPT_TEMPLATE = """Use the following context to answer the question. 
If you don't know the answer based on the context, say you don't know.

Context:
{context}

Question: {question}

Answer:"""

PROMPT = PromptTemplate(
    template=_PROMPT_TEMPLATE, input_variables=["context", "question"]
)


def get_qa_chain():
    llm = ChatOllama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
    )
    store = get_vector_store()
    retriever = store.as_retriever(search_kwargs={"k": 4})
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT},
    )
    return chain


def ask_question(question: str) -> dict:
    chain = get_qa_chain()
    result = chain.invoke({"query": question})
    sources = list(
        {doc.metadata.get("source", "unknown") for doc in result["source_documents"]}
    )
    return {"answer": result["result"], "sources": sources}
