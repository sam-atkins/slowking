"""
Mock Eigen API
"""
import random
import uuid
from datetime import datetime
from logging import getLogger

from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = getLogger(__name__)

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
def document_uploader(files: list[UploadFile]):
    # TODO add background task to "process" documents
    file_names = [file.filename for file in files]
    file_qty = len(files)
    logger.info(f"Received {file_qty} files")
    logger.info(f"File names received: {file_names}")

    # background task
    # loop over files
    #   send start upload doc event
    #   wait random number of seconds (between 1 and 5?)
    #   send end upload doc event

    return {"message": f"{file_qty} document(s) received"}
