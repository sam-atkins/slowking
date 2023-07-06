"""
Report generation adapters.
"""
import abc
import csv
import datetime
import logging.config

from slowking.domain import model

logger = logging.getLogger(__name__)


# TODO move to config, switch to docker path
# OUTPUT_DIR = "/home/app/reports"
OUTPUT_DIR = "./reports/"
OUTPUT_FILENAME = "report.csv"


# is the ABC necessary?
class AbstractReporter:
    @abc.abstractmethod
    def create(self, benchmark: model.Benchmark):
        raise NotImplementedError


class LatencyReport(AbstractReporter):
    """
    Latency report generator. Creates a CSV file with document upload times.
    """

    output_dir: str = OUTPUT_DIR
    output_filename: str = OUTPUT_FILENAME

    @classmethod
    def create(cls, benchmark: model.Benchmark):
        """
        Create report for given benchmark.
        """
        fieldnames = [
            "Benchmark Name",
            "Benchmark Type",
            "Infra",
            "Eigen Version",
            "Doc Name",
            "Upload Time (seconds)",
        ]
        base_info = {
            "Benchmark Name": benchmark.name,
            "Benchmark Type": benchmark.benchmark_type,
            "Infra": benchmark.target_infra,
            "Eigen Version": benchmark.eigen_platform_version,
        }
        fields = []
        for doc in benchmark.project.document:
            doc_info = {
                "Doc Name": doc.name,
                "Upload Time (seconds)": doc.upload_time,
            }
            fields.append({**base_info, **doc_info})
        with open(f"{cls.output_dir}{cls.output_filename}", "w") as csv_file:
            csv_writer = csv.DictWriter(
                csv_file,
                delimiter=",",
                quoting=csv.QUOTE_MINIMAL,
                fieldnames=fieldnames,
            )
            csv_writer.writeheader()
            for field in fields:
                csv_writer.writerow(field)
        logger.info("=== LatencyReport created ===")


if __name__ == "__main__":
    # TODO move to test file?
    doc = model.Document(
        name="test doc",
        file_path="test path",
    )
    doc.upload_time_start = datetime.datetime.now() - datetime.timedelta(seconds=5)
    doc.upload_time_end = datetime.datetime.now()
    doc2 = model.Document(
        name="test doc2",
        file_path="test path",
    )
    doc2.upload_time_start = datetime.datetime.now() - datetime.timedelta(seconds=2)
    doc2.upload_time_end = datetime.datetime.now()

    benchmark = model.Benchmark(
        name="test bm",
        benchmark_type="latency",
        eigen_platform_version="5.11.0-rc.1",
        target_infra="k8s",
        target_url="localhost",
        username="test user",
        password="test pw",
        project=model.Project(name="test project", document=[doc, doc2]),
    )
    LatencyReport.create(benchmark)
    # create_report(benchmark)
