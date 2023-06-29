import logging
from typing import Callable

from src.domain import commands, events

logger = logging.getLogger(__name__)


def create_benchmark(
    cmd: commands.CreateBenchmark, publish: Callable[[events.Event], None]
):
    logger.info("=== Called create_benchmark handler ===")
    logger.info(f"create_benchmark cmd: {cmd}")
    # TODO use UOW domain model to create a benchmark in the db
    # benchmark_id is the id of the benchmark created in the db
    benchmark_id = 1

    publish(
        events.BenchmarkCreated(
            channel=events.EventChannelEnum.BENCHMARK_CREATED,
            name=cmd.name,
            benchmark_id=benchmark_id,
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


# TODO inject in bootstrap
def update_document(
    cmd: commands.UpdateDocument, publish: Callable[[events.Event], None]
):
    logger.info("=== Called update_document ===")
    logger.info(f"update_document cmd: {cmd}")
    # TODO use UOW domain model to update a document in the db
    # document_id is the id of the document updated in the db
    document_id = 1

    publish(
        events.DocumentUpdated(
            channel=events.EventChannelEnum.DOCUMENT_UPDATED,
            document_id=document_id,
            document_name=cmd.document_name,
            eigen_document_id=cmd.eigen_document_id,
            eigen_project_id=cmd.eigen_project_id,
            end_time=cmd.end_time,
            start_time=cmd.start_time,
        )
    )


# TODO inject in bootstrap
def check_all_documents_uploaded(
    event: events.DocumentUpdated, publish: Callable[[events.Event], None]
):
    logger.info("=== Called check_all_documents_uploaded ===")
    logger.info(f"check_all_documents_uploaded event: {event}")
    # TODO handler event DocumentUpdated
    # check if all docs are updated, if so, send event for next stage in benchmark
    # create report?
