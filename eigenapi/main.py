"""
Mock Eigen API
"""
import logging
import random
import time
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Annotated

import requests
from fastapi import BackgroundTasks, FastAPI, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI()

# this would be part of config, set on the benchmark host/target
BENCHMARK_HOST_NAME = "eigenapi:8283"
# SLOWKING_HOST_NAME = "slowking:8091"
SLOWKING_HOST_NAME = "slowking-api-eventbus:8091"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/v1/token/")
def auth_token():
    content = {"message": "Come to the dark side, we have cookies"}
    response = JSONResponse(content=content)
    response.set_cookie(key="fakesession", value="fake-cookie-session-value")
    return response


class ProjectItem(BaseModel):
    name: str
    description: str | None


@app.post("/api/project_management/v2/projects/")
def create_project(item: ProjectItem):
    """
    Provides a mock response for the Eigen create project endpoint
    """
    project_id = random.randint(1, 100)
    data = {
        "guid": str(uuid.uuid4()),
        "document_type_id": project_id,
        "name": item.name,
        "description": item.description,
        "created_at": datetime.now(timezone.utc).timestamp(),
        "language": "english",
        "use_numerical_confidence_predictions": True,
    }
    return JSONResponse(content=data)


@app.post("/api/v1/document_uploader/")
async def document_uploader(
    document_type_id: Annotated[str, Form()],
    files: list[UploadFile],
    background_tasks: BackgroundTasks,
):
    file_names = [file.filename for file in files]
    file_qty = len(files)

    # TODO not logging to stdout, why not?
    logger.info(f"Received {file_qty} files")
    logger.info(f"File names received: {file_names}")

    # HACK to get around logging not working
    print(f"{document_type_id=}")
    print(f"Received {file_qty} files")
    print(f"File names received: {file_names}")

    background_tasks.add_task(fake_document_uploader, files, document_type_id)

    return {"message": f"{file_qty} document(s) received"}, HTTPStatus.ACCEPTED


def fake_document_uploader(files: list[UploadFile], document_type_id: str):
    """
    Instrumentation faker. Sends fake commands to the eventbus when
    a document upload starts and again when it ends.
    """
    fake_doc_id = 10
    for _file in files:
        # hack to avoid typing errors, if a file was malformed/incorrect, we'd
        # want to log and/or raise an error
        if not _file.filename:
            continue
        doc_start_time = datetime.now(timezone.utc).timestamp()
        send_command_to_eventbus(
            filename=_file.filename,
            eigen_project_id=document_type_id,
            eigen_document_id=fake_doc_id,
            start_time=doc_start_time,
        )
        time.sleep(random.randint(1, 5))
        doc_end_time = datetime.now(timezone.utc).timestamp()
        send_command_to_eventbus(
            filename=_file.filename,
            eigen_project_id=document_type_id,
            eigen_document_id=fake_doc_id,
            end_time=doc_end_time,
        )
        fake_doc_id += 1


class UpdateDocument(BaseModel):
    document_name: str
    eigen_document_id: str
    eigen_project_id: str
    benchmark_host_name: str
    end_time: float | None  # TODO: change to datetime
    start_time: float | None  # TODO: change to datetime


def send_command_to_eventbus(
    filename: str,
    eigen_project_id: str,
    eigen_document_id: int,
    start_time: float | None = None,
    end_time: float | None = None,
):
    payload = UpdateDocument(
        document_name=filename,
        eigen_document_id=str(eigen_document_id),
        eigen_project_id=eigen_project_id,
        benchmark_host_name=BENCHMARK_HOST_NAME,
        start_time=start_time,
        end_time=end_time,
    )

    endpoint = "/api/v1/benchmarks/documents/"
    url = f"http://{SLOWKING_HOST_NAME}{endpoint}"
    print(f"Sending command to {url} - payload: {payload}")

    response = requests.post(url, json=payload.dict())
    print(f"Response from {url}: {response}")
