"""
Mock Eigen API
"""
import random

from fastapi import FastAPI, Response

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/auth/v1/token/")
def auth_token():
    return Response(content="token")


@app.post("/api/project_management/v2/projects")
def create_project():
    project_id = random.randint(1, 100)
    # TODO data shape of the response?
    data = {"project_id": project_id}
    return Response(content=data)


@app.post("api/v1/document_uploader/")
def document_uploader():
    # TODO add background task to "process" documents
    return Response(content="document uploaded")
