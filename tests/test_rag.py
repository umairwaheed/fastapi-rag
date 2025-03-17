from unittest.mock import MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import Chunk


def test_post_upload_text(
    client: TestClient, sample_text, session: Session, user_token: str
):
    response = client.post(
        "/rag/upload/",
        json={"text": sample_text},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "document_id" in data

    chunks = session.exec(
        select(Chunk).where(Chunk.document_id == data["document_id"])
    ).all()
    assert len(chunks) == 1
    assert chunks[0].chunk_text == sample_text


@patch("openai.chat.completions.create")
def test_post_query_text(mock_openai, client: TestClient, user_token: str):
    mock_openai.return_value = MagicMock()
    mock_openai.return_value.choices = [
        MagicMock(message=MagicMock(content="This is a mocked response from OpenAI."))
    ]

    response = client.post(
        "/rag/query/",
        json={"text": "What is the document about?"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] == "This is a mocked response from OpenAI."
    assert "context" in data
