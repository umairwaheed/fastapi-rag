from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import Chunk


def test_upload_text(client: TestClient, sample_text, session: Session):
    response = client.post("/rag/upload/", json={"text": sample_text})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "document_id" in data

    chunks = session.exec(
        select(Chunk).where(Chunk.document_id == data["document_id"])
    ).all()
    assert len(chunks) == 1
    assert chunks[0].chunk_text == sample_text
