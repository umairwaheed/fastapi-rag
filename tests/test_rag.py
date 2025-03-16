from fastapi import status
from fastapi.testclient import TestClient


def test_upload_text(client: TestClient, sample_text):
    response = client.post("/rag/upload/", json={"text": sample_text})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "document_id" in data
