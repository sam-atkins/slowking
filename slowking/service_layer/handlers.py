import logging
import pathlib
import time
from datetime import datetime, timezone
from typing import Callable, Type

from sqlalchemy.exc import IllegalStateChangeError, InvalidRequestError
from sqlalchemy.orm.exc import DetachedInstanceError

from slowking.adapters import notifications
from slowking.adapters.http import EigenClient
from slowking.adapters.report import LatencyReport
from slowking.config import settings
from slowking.domain import benchmarks, commands, events, model
from slowking.service_layer import unit_of_work

logger = logging.getLogger(__name__)


def create_benchmark(
    cmd: commands.CreateBenchmark,
    uow: unit_of_work.AbstractUnitOfWork,
    publish: Callable[[events.Event], None],
):
    logger.info("=== Called create_benchmark handler ===")

    name = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d, %H:%M:%S')} - {cmd.name}"

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
            password=cmd.password,
            project=project,
        )
        uow.benchmarks.add(bm)
        uow.flush()
        benchmark = uow.benchmarks.get_by_name(name)
        logger.info(f"=== create_benchmark :: benchmark.id === : {benchmark.id}")

        next_event = benchmarks.get_next_event(
            benchmark_id=benchmark.id,
            benchmark_type=benchmark.benchmark_type,
            current_message=cmd,
        )
        if next_event is None:
            logger.info("=== No next event ===")
            return

        publish(next_event)


def create_project(
    event: events.BenchmarkCreated,
    uow: unit_of_work.AbstractUnitOfWork,
    publish: Callable[[events.Event], None],
    client: type[EigenClient],
):
    logger.info("=== Called create_project ===")
    logger.info(f"create_project event: {event}")

    with uow:
        benchmark = uow.benchmarks.get_by_id(event.benchmark_id)

        eigen = client(
            base_url=benchmark.target_url,
            username=benchmark.username,
            password=benchmark.password,
        )
        project = eigen.create_project(
            name=benchmark.name, description=benchmark.benchmark_type
        )
        logger.info(f"=== create_project :: project response === : {project}")
        project_id = project.document_type_id

        benchmark.project.eigen_project_id = project_id
        logger.info(f"===  benchmark.project === : {benchmark.project}")
        uow.benchmarks.add(benchmark)
        uow.flush()
        logger.info("=== Create Project completed ===")

        next_event = benchmarks.get_next_event(
            benchmark_id=benchmark.id,
            benchmark_type=benchmark.benchmark_type,
            current_message=event,
        )
        if next_event is None:
            logger.info("=== No next event ===")
            return

        logger.info(f"=== next_event === : {next_event}")
        publish(next_event)


def upload_documents(
    event: events.ProjectCreated,
    client: Type[EigenClient],
    uow: unit_of_work.AbstractUnitOfWork,
):
    logger.info("=== Called upload_documents ===")
    logger.info(f"upload_documents event: {event}")
    # TODO using hardcoded artifacts dir to get docs for upload, move to settings
    files = pathlib.Path("/home/app/artifacts").glob("*.txt")
    logger.info(f"=== upload_documents :: found files === : {files}")
    f_list = list(files.__iter__())
    logger.info(f"=== upload_documents :: f_list === : {f_list}")

    with uow:
        benchmark = uow.benchmarks.get_by_id(event.benchmark_id)

        eigen = client(
            base_url=benchmark.target_url,
            username=benchmark.username,
            password=benchmark.password,
        )
        response = eigen.upload_files(
            project_id=benchmark.project.eigen_project_id, files=f_list
        )
        logger.info(f"=== upload_documents :: response === : {response}")
        logger.info("=== Upload Documents completed ===")


def update_document(
    cmd: commands.UpdateDocument,
    uow: unit_of_work.AbstractUnitOfWork,
    publish: Callable[[events.Event], None],
):
    logger.info("=== Called update_document ===")
    logger.info(f"update_document cmd: {cmd}")

    for _ in range(0, settings.DB_MAX_RETRIES):
        try:
            with uow:
                bm = uow.benchmarks.get_by_host_and_project_id(
                    host=cmd.benchmark_host_name, project_id=int(cmd.eigen_project_id)
                )
                logger.info(f"=== bm === : {bm}")

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

                next_event = benchmarks.get_next_event(
                    benchmark_id=bm.id,
                    benchmark_type=bm.benchmark_type,
                    current_message=cmd,
                )
                if next_event is None:
                    logger.info("=== No next event ===")
                    return

                publish(next_event)

        except (DetachedInstanceError, IllegalStateChangeError, InvalidRequestError):
            logger.info(
                f"===DB exception when updating doc {cmd.document_name}, retrying."
            )
            time.sleep(settings.DB_RETRY_INTERVAL)


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

            next_event = benchmarks.get_next_event(
                benchmark_id=bm.id,
                benchmark_type=bm.benchmark_type,
                current_message=event,
            )
            if next_event is None:
                logger.info("=== No next event ===")
                return

            publish(next_event)


def create_report(
    event: events.AllDocumentsUploaded,
    uow: unit_of_work.AbstractUnitOfWork,
    notifications: notifications.AbstractNotifications,
):
    logger.info(f"=== Called create_report with {event} ===")
    with uow:
        bm = uow.benchmarks.get_by_id(event.benchmark_id)
        logger.info(f"=== create_report bm === : {bm}")
        LatencyReport().create(bm)
        notifications.send(bm, "Benchmark report generated")
        logger.info("=== Create Report Notification sent  ===")
