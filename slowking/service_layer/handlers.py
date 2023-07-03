import logging
import pathlib
from datetime import datetime
from typing import Callable

from slowking.adapters.http import EigenClient
from slowking.domain import commands, events, model
from slowking.service_layer import unit_of_work

logger = logging.getLogger(__name__)


def create_benchmark(
    cmd: commands.CreateBenchmark,
    uow: unit_of_work.AbstractUnitOfWork,
    publish: Callable[[events.Event], None],
):
    logger.info("=== Called create_benchmark handler ===")

    name = f"{datetime.now().strftime('%Y-%m-%d, %H:%M:%S')} - {cmd.name}"
    # NOTE placeholder for benchmark.id to avoid DetachedInstanceError Session issues
    benchmark_id: int

    with uow:
        project = model.Project(name=name)
        bm = model.Benchmark(
            name=name,
            benchmark_type=cmd.benchmark_type,
            release_version=cmd.target_release_version,
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
        uow.commit()

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


def create_project(
    event: events.BenchmarkCreated,
    uow: unit_of_work.AbstractUnitOfWork,
    publish: Callable[[events.Event], None],
):
    logger.info("=== Called create_project ===")
    logger.info(f"create_project event: {event}")

    client = EigenClient(
        base_url=event.target_url,
        username=event.username,
        password=event.password.get_secret_value(),
    )
    project = client.create_project(name=event.name, description=event.benchmark_type)
    logger.info(f"=== create_project :: project response === : {project}")
    project_id = project.document_type_id

    with uow:
        benchmark = uow.benchmarks.get_by_id(event.benchmark_id)
        benchmark.project.eigen_project_id = project_id
        logger.info(f"===  benchmark.project === : {benchmark.project}")
        uow.benchmarks.add(benchmark)
        uow.commit()

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


def upload_documents(event: events.ProjectCreated):
    logger.info("=== Called upload_documents ===")
    logger.info(f"upload_documents event: {event}")
    # use hardcoded artifacts dir to get docs for upload
    files = pathlib.Path("/home/app/artifacts").glob("*.txt")
    logger.info(f"=== upload_documents :: found files === : {files}")
    f_list = list(files.__iter__())
    logger.info(f"=== upload_documents :: f_list === : {f_list}")

    # get benchmark from db? need id? or get from event

    # use EigenClient to upload documents
    client = EigenClient(
        base_url=event.target_url,
        username=event.username,
        password=event.password.get_secret_value(),
    )
    response = client.upload_files(project_id=event.eigen_project_id, files=f_list)
    logger.info(f"=== upload_documents :: response === : {response}")
    # end


def update_document(
    cmd: commands.UpdateDocument,
    uow: unit_of_work.AbstractUnitOfWork,
    publish: Callable[[events.Event], None],
):
    logger.info("=== Called update_document ===")
    logger.info(f"update_document cmd: {cmd}")
    # TODO use UOW domain model to update a document in the db
    # document_id is the id of the document updated in the db
    # document_id = 1

    # All WIP, not tested
    # doc = model.Document(
    #     name=cmd.document_name,
    #     file_path="",
    #     eigen_document_id=cmd.eigen_document_id,
    #     eigen_project_id=cmd.eigen_project_id,
    #     # end_time=cmd.end_time,
    #     # start_time=cmd.start_time,
    # )
    # # TODO fix type warnings
    # doc.upload_time_start = cmd.start_time
    # doc.upload_time_end = cmd.end_time

    # with uow:
    #     bm = uow.benchmarks.get_by_document_name_and_project_id(
    #         name=cmd.document_name, project_id=cmd.eigen_project_id
    #     )
    #     logger.info(f"=== bm === : {bm}")

    #     # NOTE, `benchmark.project.documents` will raise if there are no documents
    #     try:
    #         bm.project.documents.append(doc)
    #     except Exception as e:
    #         logger.exception(e)
    #     uow.benchmarks.add(bm)

    # publish(
    #     events.DocumentUpdated(
    #         channel=events.EventChannelEnum.DOCUMENT_UPDATED,
    #         document_id=cmd.eigen_document_id,  # fix name and int or str
    #         document_name=cmd.document_name,
    #         eigen_project_id=cmd.eigen_project_id,
    #         # end_time=cmd.end_time,
    #         # start_time=cmd.start_time,
    #     )
    # )


def check_all_documents_uploaded(
    event: events.DocumentUpdated,
    uow: unit_of_work.AbstractUnitOfWork,
    publish: Callable[[events.Event], None],
):
    logger.info("=== Called check_all_documents_uploaded ===")
    logger.info(f"check_all_documents_uploaded event: {event}")
    # TODO handler event DocumentUpdated
    # check if all docs are updated, if so, send event for next stage in benchmark
    # create report?
