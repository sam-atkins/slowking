"""
API Router
"""
from fastapi import FastAPI

from src.entrypoints.http import router

app = FastAPI()
app.include_router(router)

version = "v1"
prefix = f"/api/{version}"


@app.get(f"{prefix}/health")
def health():
    return {"status": "ok"}
