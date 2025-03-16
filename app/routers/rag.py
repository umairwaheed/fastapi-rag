import os

import openai
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.dependencies import get_session
from app.helpers import chunk_text, create_embedding
from app.models import Chunk, Document

router = APIRouter()

client = openai.Client()
client.api_key = os.getenv("OPENAI_API_KEY")


@router.post("/upload/")
def upload_text(document: Document, session: Session = Depends(get_session)):
    session.add(document)
    session.commit()
    session.refresh(document)

    chunks = chunk_text(document.text)
    for chunk in chunks:
        embedding = create_embedding(chunk)
        chunk_entry = Chunk(
            document_id=document.id, chunk_text=chunk, embedding=embedding
        )
        session.add(chunk_entry)

    session.commit()
    return {
        "message": "Text uploaded and processed successfully",
        "document_id": document.id,
    }


@router.post("/query/")
def query_text(query: str, session: Session = Depends(get_session)):
    query_embedding = create_embedding(query)

    stmt = select(Chunk).order_by(Chunk.embedding.op("<=>")(query_embedding)).limit(3)
    top_chunks = session.exec(stmt).all()

    if not top_chunks:
        raise HTTPException(status_code=404, detail="No relevant documents found")

    context = "\n".join([chunk.chunk_text for chunk in top_chunks])

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Answer the question based on the provided context.",
            },
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
    )

    answer = response.choices[0].message.content
    return {"answer": answer, "context": [chunk.chunk_text for chunk in top_chunks]}
