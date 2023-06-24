"""
API Entrypoints for the Eventbus application
"""
import logging.config
from http import HTTPStatus
from logging import getLogger

from fastapi import BackgroundTasks, FastAPI, Request, Response
from pydantic import BaseModel

from src import bootstrap, config
from src.adapters.redis_event_publisher import publish
from src.domain import commands

app = FastAPI()
bus = bootstrap.bootstrap()

logging.config.dictConfig(config.logger_dict_config())
logger = getLogger(__name__)

v1 = "/api/v1"


def publish_to_bus(cmd: commands.Command):
    """
    Publishes a command to the eventbus
    """
    bus.handle(cmd)


@app.get(f"{v1}/channels")
def channels():
    channels = config.get_redis_subscribe_channels()
    return {"channels": channels}


@app.get(f"{v1}/health")
def health():
    return {"status": "healthy"}


@app.post(f"{v1}/events/publish")
async def publish_event(request: Request, background_tasks: BackgroundTasks):
    """
    Publish an event to the eventbus
    """
    payload = await request.json()
    channel = payload.get("channel")
    logger.info(f"API /events/publish publishing message to channel: {channel}")
    background_tasks.add_task(publish, payload)

    return Response(status_code=HTTPStatus.ACCEPTED)


class BenchmarkPayload(BaseModel):
    name: str
    benchmark_type: str
    target_infra: str
    target_url: str
    target_release_version: str
    username: str
    password: str


@app.post(f"{v1}/benchmarks/start")
async def start_benchmark(payload: BenchmarkPayload, background_tasks: BackgroundTasks):
    logger.info(f"API /benchmarks/start starting benchmark: {payload.name}")
    cmd = commands.CreateBenchmark(
        channel=commands.CommandChannelEnum.CREATE_BENCHMARK,
        name=payload.name,
        benchmark_type=payload.benchmark_type,
        target_infra=payload.target_infra,
        target_url=payload.target_url,
        target_release_version=payload.target_release_version,
        username=payload.username,
        password=payload.password, # type: ignore
    )
    background_tasks.add_task(publish_to_bus, cmd)
    return Response(status_code=HTTPStatus.ACCEPTED)
