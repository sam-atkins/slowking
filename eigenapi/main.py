"""
Mock Eigen API
"""
import logging
import random
import uuid
from datetime import datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import BackgroundTasks, FastAPI, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI()


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
        "created_at": datetime.utcnow().timestamp(),
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
    pass
    # TODO
    # needed to send commands to the eventbus
    # eigen_project_id & target_url (host) so document can be assigned to the correct bm
    # eigen_document_id - this is available, provide a fake int that increments
    # eigen_document_name - this is available: f.name

    # loop over files
    #   send *start* upload doc event
    #   wait random number of seconds (between 1 and 5?)
    #   send *end* upload doc event
