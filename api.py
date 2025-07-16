# api.py – v2.2

from fastapi import FastAPI, Query
from pydantic import BaseModel
from s3ai_query import answer_question

app = FastAPI(title="S3 On-Prem AI Assistant", description="Ask questions to your Cloudian/MinIO/IBM S3 docs.")

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    result = answer_question(req.question)
    return {"answer": result}
