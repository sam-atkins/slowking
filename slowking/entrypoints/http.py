"""
HTTP entrypoints for the Eventbus application
"""
import logging.config
from http import HTTPStatus
from logging import getLogger

from fastapi import APIRouter, BackgroundTasks, Response
from pydantic import BaseModel

from slowking import bootstrap, config
from slowking.config import settings
from slowking.domain import commands

router = APIRouter(prefix=settings.API_BENCHMARK_NAMESPACE_V1_STR, tags=["benchmarks"])


logging.config.dictConfig(config.logger_dict_config())
logger = getLogger(__name__)


def publish_to_bus(cmd: commands.Command):
    """
    Publishes a command to the eventbus
    """
    bus = bootstrap.bootstrap()
    bus.handle(cmd)


@router.get("/channels")
def channels():
    return {"channels": settings.REDIS_SUBSCRIBE_CHANNELS}


class BenchmarkPayload(BaseModel):
    name: str
    benchmark_type: str
    target_infra: str
    target_url: str
    target_eigen_platform_version: str
    username: str
    password: str


@router.post("/start", status_code=HTTPStatus.ACCEPTED)
async def start_benchmark(payload: BenchmarkPayload, background_tasks: BackgroundTasks):
    logger.info(f"API /benchmarks/start starting benchmark: {payload.name}")
    cmd = commands.CreateBenchmark(
        channel=commands.CommandChannelEnum.CREATE_BENCHMARK,
        name=payload.name,
        benchmark_type=payload.benchmark_type,
        target_infra=payload.target_infra,
        target_url=payload.target_url,
        target_eigen_platform_version=payload.target_eigen_platform_version,
        username=payload.username,
        password=payload.password,  # type: ignore
    )
    background_tasks.add_task(publish_to_bus, cmd)
    return Response(status_code=HTTPStatus.ACCEPTED)


class UpdateDocumentPayload(BaseModel):
    document_name: str
    eigen_document_id: str
    eigen_project_id: str
    benchmark_host_name: str
    end_time: float | None  # TODO: type is a datetime timestamp
    start_time: float | None  # TODO: type is a datetime timestamp


@router.post("/documents/", status_code=HTTPStatus.ACCEPTED)
async def update_document(
    payload: UpdateDocumentPayload, background_tasks: BackgroundTasks
):
    """
    Update document in a benchmark by issuing an `UpdateDocument` command.
    The command is published to the eventbus to be handled.
    """
    logger.info(f"API /benchmarks/document/ updating {payload.document_name}")
    cmd = commands.UpdateDocument(
        channel=commands.CommandChannelEnum.UPDATE_DOCUMENT,
        document_name=payload.document_name,
        eigen_document_id=payload.eigen_document_id,
        eigen_project_id=payload.eigen_project_id,
        benchmark_host_name=payload.benchmark_host_name,
        end_time=payload.end_time,
        start_time=payload.start_time,
    )
    background_tasks.add_task(publish_to_bus, cmd)
    return Response(status_code=HTTPStatus.ACCEPTED)
