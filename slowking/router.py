"""
API Router
"""
from fastapi import FastAPI

from slowking.config import settings
from slowking.entrypoints.http import router

app = FastAPI()
app.include_router(router)


@app.get(f"{settings.API_V1_STR}/health")
def health():
    return {"status": "ok"}
