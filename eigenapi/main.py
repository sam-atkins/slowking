"""
Mock Eigen API
"""
from fastapi import FastAPI, Response

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


# endpoints:
# auth token: auth/v1/token/
# create project
# url = urljoin({base_url}api/project_management/v2/, "projects")
# doc uploader: url = f"{self.base_url_v1}document_uploader/"


@app.get("/auth/v1/token/")
def auth_token():
    return Response(content="token")
