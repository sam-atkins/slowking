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

logging.config.dictConfig(config.logger_dict_config())
logger = getLogger(__name__)

v1 = "/api/v1"


@app.get(f"{v1}/health")
def health():
    return {"status": "healthy"}


@app.get(f"{v1}/events/channels")
def channels():
    channels = config.get_redis_subscribe_channels()
    return {"channels": channels}


@app.post(f"{v1}/events/publish")
async def event(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    channel = payload.get("channel")
    logger.info(f"API payload.channel: {channel}")
    background_tasks.add_task(publish, payload)

    return Response(status_code=HTTPStatus.ACCEPTED)


def publish_to_bus(cmd):
    bus = bootstrap.bootstrap()
    bus.handle(cmd)


class CustomerRequestBody(BaseModel):
    first_name: str
    surname: str


@app.post(f"{v1}/customers")
async def create_customer(body: CustomerRequestBody, background_tasks: BackgroundTasks):
    logger.info(f"creating customer {body.first_name} {body.surname}")
    cmd = commands.CreateCustomer(
        channel=commands.CommandChannelEnum.CREATE_CUSTOMER,
        first_name=body.first_name,
        surname=body.surname,
    )
    background_tasks.add_task(publish_to_bus, cmd)
    return Response(status_code=HTTPStatus.ACCEPTED)
