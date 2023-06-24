import logging
from typing import Callable, Type

from src.domain import commands, events

logger = logging.getLogger(__name__)


def create_benchmark(cmd: commands.CreateBenchmark, publish: Callable):
    logger.info("=== Called create_benchmark handler ===")
    logger.info(f"create_benchmark cmd: {cmd}")
    # TODO use UOW domain model to create a benchmark in the db

    publish(
        events.BenchmarkCreated(
            channel=events.EventChannelEnum.BENCHMARK_CREATED,
            name=cmd.name,
            benchmark_type=cmd.benchmark_type,
            target_infra=cmd.target_infra,
            target_url=cmd.target_url,
            target_release_version=cmd.target_release_version,
            username=cmd.username,
            password=cmd.password,
        )
    )


def get_artifacts(event: events.BenchmarkCreated):
    logger.info("=== Called get_artifacts ===")
    logger.info(f"get_artifacts event: {event}")


def create_project(event: events.BenchmarkCreated):
    logger.info("=== Called create_project ===")
    logger.info(f"create_project event: {event}")


def upload_documents(event: events.ProjectCreated):
    logger.info("=== Called upload_documents ===")
    logger.info(f"upload_documents event: {event}")
