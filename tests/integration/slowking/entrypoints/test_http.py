from fastapi.testclient import TestClient

from slowking.entrypoints.http import router

client = TestClient(router)


def test_channels_endpoint():
    response = client.get("/api/v1/benchmarks/channels")
    assert response.status_code == 200
    assert response.json() == {
        "channels": [
            "all_documents_uploaded",
            "benchmark_created",
            "document_updated",
            "project_created",
            "create_benchmark",
            "update_document",
        ]
    }
