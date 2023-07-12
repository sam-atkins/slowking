from http import HTTPStatus
from unittest.mock import patch

import pytest
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient

from slowking.entrypoints.http import router

client = TestClient(router)


def test_channels_endpoint():
    response = client.get("/api/v1/benchmarks/channels")
    assert response.status_code == HTTPStatus.OK
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


@patch("fastapi.BackgroundTasks.add_task")
def test_start_benchmark_endpoint_accepted(mock_add_task):
    payload = {
        "name": "test-benchmark",
        "benchmark_type": "latency",
        "target_infra": "k8s",
        "target_url": "localhost",
        "target_eigen_platform_version": "5.11.0-rc.1",
        "username": "test user",
        "password": "test pw",
    }
    response = client.post("/api/v1/benchmarks/start", json=payload)
    assert response.status_code == HTTPStatus.ACCEPTED


def test_start_benchmark_endpoint_unprocessable_entity():
    payload = {
        "name": "test-benchmark",
        "benchmark_type": "latency",
        "target_infra": "k8s",
        "target_url": "localhost",
        "target_eigen_platform_version": "5.11.0-rc.1",
    }
    with pytest.raises(RequestValidationError):
        response = client.post("/api/v1/benchmarks/start", json=payload)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@patch("fastapi.BackgroundTasks.add_task")
def test_update_document_endpoint_accepted_with_start_time(mock_add_task):
    payload = {
        "document_name": "test doc",
        "eigen_document_id": "11",
        "eigen_project_id": "22",
        "benchmark_host_name": "test host",
        "start_time": 123.456,
    }
    response = client.post("/api/v1/benchmarks/documents", json=payload)
    assert response.status_code == HTTPStatus.ACCEPTED


@patch("fastapi.BackgroundTasks.add_task")
def test_update_document_endpoint_accepted_with_end_time(mock_add_task):
    payload = {
        "document_name": "test doc",
        "eigen_document_id": "11",
        "eigen_project_id": "22",
        "benchmark_host_name": "test host",
        "end_time": 123.456,
    }
    response = client.post("/api/v1/benchmarks/documents", json=payload)
    assert response.status_code == HTTPStatus.ACCEPTED


def test_update_document_endpoint_unprocessable_entity():
    payload = {
        "document_name": "test doc",
        "eigen_project_id": "22",
        "benchmark_host_name": "test host",
    }
    with pytest.raises(RequestValidationError):
        response = client.post("/api/v1/benchmarks/documents", json=payload)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
