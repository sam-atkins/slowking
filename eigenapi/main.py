"""
Mock Eigen API
"""
import random
from logging import getLogger

from fastapi import FastAPI
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
    project_id = random.randint(1, 100)
    # TODO data shape of the response?
    data = {"project_id": project_id}
    return JSONResponse(content=data)


# @app.post("api/v1/document_uploader/")
# def document_uploader(files: list[UploadFile]):
#     # TODO add background task to "process" documents
#     file_names = [file.filename for file in files]
#     logger.info(f"Received {len(files)} files")
#     logger.info(f"File names received: {file_names}")

#     # background task
#     # loop over files
#     #   send start upload doc event
#     #   wait random number of seconds (between 1 and 5?)
#     #   send end upload doc event

#     return Response(content="document(s) received")
