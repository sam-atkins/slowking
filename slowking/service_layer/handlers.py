import logging
import pathlib
import time
from datetime import datetime, timezone
from typing import Callable, Type

from sqlalchemy.exc import IllegalStateChangeError, InvalidRequestError
from sqlalchemy.orm.exc import DetachedInstanceError

from slowking.adapters.http import EigenClient
from slowking.adapters.report import LatencyReport
from slowking.config import settings
from slowking.domain import commands, events, model
from slowking.service_layer import unit_of_work

logger = logging.getLogger(__name__)


def create_benchmark(
    cmd: commands.CreateBenchmark,
    uow: unit_of_work.AbstractUnitOfWork,
    publish: Callable[[events.Event], None],
):
    logger.info("=== Called create_benchmark handler ===")

    name = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d, %H:%M:%S')} - {cmd.name}"
    # NOTE placeholder for benchmark.id to avoid DetachedInstanceError Session issues
    benchmark_id: int

    with uow:
        documents = []
        files = pathlib.Path("/home/app/artifacts").glob("*.txt")
        for file in files:
            documents.append(
                model.Document(
                    name=file.name,
                    file_path=str(file),
                )
            )
        project = model.Project(name=name, document=documents)
        bm = model.Benchmark(
            name=name,
            benchmark_type=cmd.benchmark_type,
            eigen_platform_version=cmd.target_eigen_platform_version,
            target_infra=cmd.target_infra,
            target_url=cmd.target_url,
            username=cmd.username,
            password=cmd.password.get_secret_value(),
            project=project,
        )
        uow.benchmarks.add(bm)
        uow.flush()
        benchmark = uow.benchmarks.get_by_name(name)
        logger.info(f"=== benchmark === : {benchmark}")
        benchmark_id = benchmark.id
        logger.info(f"=== create_benchmark :: benchmark.id === : {benchmark.id}")

    publish(
        events.BenchmarkCreated(
            channel=events.EventChannelEnum.BENCHMARK_CREATED,
            name=cmd.name,
            benchmark_id=benchmark_id,
            benchmark_type=cmd.benchmark_type,
            target_infra=cmd.target_infra,
            target_url=cmd.target_url,
            target_eigen_platform_version=cmd.target_eigen_platform_version,
            username=cmd.username,
            password=cmd.password,
        )
    )


def get_artifacts(event: events.BenchmarkCreated):
    logger.info("=== Called get_artifacts ===")
    logger.info(f"get_artifacts event: {event}")


def create_project(
    event: events.BenchmarkCreated,
    uow: unit_of_work.AbstractUnitOfWork,
    publish: Callable[[events.Event], None],
    client: type[EigenClient],
):
    logger.info("=== Called create_project ===")
    logger.info(f"create_project event: {event}")

    eigen = client(
        base_url=event.target_url,
        username=event.username,
        password=event.password.get_secret_value(),
    )
    project = eigen.create_project(name=event.name, description=event.benchmark_type)
    logger.info(f"=== create_project :: project response === : {project}")
    project_id = project.document_type_id

    with uow:
        benchmark = uow.benchmarks.get_by_id(event.benchmark_id)
        benchmark.project.eigen_project_id = project_id
        logger.info(f"===  benchmark.project === : {benchmark.project}")
        uow.benchmarks.add(benchmark)

    logger.info("=== Create Project completed ===")
    publish(
        events.ProjectCreated(
            channel=events.EventChannelEnum.PROJECT_CREATED,
            eigen_project_id=project_id,
            password=event.password,
            username=event.username,
            target_url=event.target_url,
        )
    )


def upload_documents(
    event: events.ProjectCreated,
    client: Type[EigenClient],
):
    logger.info("=== Called upload_documents ===")
    logger.info(f"upload_documents event: {event}")
    # TODO using hardcoded artifacts dir to get docs for upload, move to settings
    files = pathlib.Path("/home/app/artifacts").glob("*.txt")
    logger.info(f"=== upload_documents :: found files === : {files}")
    f_list = list(files.__iter__())
    logger.info(f"=== upload_documents :: f_list === : {f_list}")

    eigen = client(
        base_url=event.target_url,
        username=event.username,
        password=event.password.get_secret_value(),
    )
    response = eigen.upload_files(project_id=event.eigen_project_id, files=f_list)
    logger.info(f"=== upload_documents :: response === : {response}")
    logger.info("=== Upload Documents completed ===")


def update_document(
    cmd: commands.UpdateDocument,
    uow: unit_of_work.AbstractUnitOfWork,
    publish: Callable[[events.Event], None],
):
    logger.info("=== Called update_document ===")
    logger.info(f"update_document cmd: {cmd}")
    benchmark_id: int

    for _ in range(0, settings.DB_MAX_RETRIES):
        try:
            with uow:
                bm = uow.benchmarks.get_by_host_and_project_id(
                    host=cmd.benchmark_host_name, project_id=int(cmd.eigen_project_id)
                )
                logger.info(f"=== bm === : {bm}")
                benchmark_id = bm.id

                documents = bm.project.document
                logger.info(f"=== documents === : {documents}")
                for doc in documents:
                    if doc.name == cmd.document_name:
                        logger.info(f"=== doc === : {doc}")
                        if cmd.start_time:
                            doc.upload_time_start = datetime.fromtimestamp(
                                cmd.start_time
                            )
                        if cmd.end_time:
                            doc.upload_time_end = datetime.fromtimestamp(cmd.end_time)
                        logger.info(f"=== doc updated === : {doc}")
                        break

                uow.benchmarks.add(bm)
        except (DetachedInstanceError, IllegalStateChangeError, InvalidRequestError):
            logger.info(
                f"===DB exception when updating doc {cmd.document_name}, retrying."
            )
            time.sleep(settings.DB_RETRY_INTERVAL)

    publish(
        events.DocumentUpdated(
            channel=events.EventChannelEnum.DOCUMENT_UPDATED,
            benchmark_id=benchmark_id,
            eigen_document_id=int(cmd.eigen_document_id),
            document_name=cmd.document_name,
            eigen_project_id=int(cmd.eigen_project_id),
        )
    )


def check_all_documents_uploaded(
    event: events.DocumentUpdated,
    uow: unit_of_work.AbstractUnitOfWork,
    publish: Callable[[events.Event], None],
):
    logger.info("=== Called check_all_documents_uploaded ===")
    logger.info(f"check_all_documents_uploaded event: {event}")

    with uow:
        bm = uow.benchmarks.get_by_id(event.benchmark_id)
        logger.info(f"=== check_all_documents_uploaded bm === : {bm}")
        documents = bm.project.document

        docs_with_upload_time = [
            doc.upload_time for doc in documents if doc.upload_time
        ]
        logger.info(f"=== docs_with_upload_time === : {docs_with_upload_time}")
        logger.info(
            f"=== len(docs_with_upload_time) === : {len(docs_with_upload_time)}"
        )
        logger.info(f"=== len(documents) === : {len(documents)}")

        if len(docs_with_upload_time) == len(documents):
            logger.info(f"=== docs_with_upload_time === : {docs_with_upload_time}")
            publish(
                events.AllDocumentsUploaded(
                    channel=events.EventChannelEnum.ALL_DOCUMENTS_UPLOADED,
                    benchmark_id=event.benchmark_id,
                )
            )


def create_report(
    event: events.AllDocumentsUploaded, uow: unit_of_work.AbstractUnitOfWork
):
    logger.info(f"=== Called create_report with {event} ===")
    with uow:
        bm = uow.benchmarks.get_by_id(event.benchmark_id)
        logger.info(f"=== create_report bm === : {bm}")
        LatencyReport().create(bm)
        # TODO notify user of report generation e.g. email with report
