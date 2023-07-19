"""
Report generation adapters.
"""
import abc
import csv
import logging.config

from slowking.config import settings
from slowking.domain import model

logger = logging.getLogger(__name__)


class AbstractReporter:
    @abc.abstractmethod
    def create(self, benchmark: model.Benchmark) -> str:
        raise NotImplementedError


class LatencyReport(AbstractReporter):
    """
    Latency report generator. Creates a CSV file with document upload times.
    """

    output_dir: str = settings.OUTPUT_DIR
    output_filename: str = settings.OUTPUT_FILENAME

    @classmethod
    def create(cls, benchmark: model.Benchmark) -> str:
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
        file_path = f"{cls.output_dir}{cls.output_filename}"
        with open(file_path, "w") as csv_file:
            csv_writer = csv.DictWriter(
                csv_file,
                delimiter=",",
                quoting=csv.QUOTE_MINIMAL,
                fieldnames=fieldnames,
            )
            csv_writer.writeheader()
            csv_writer.writerows(fields)
        logger.info(f"=== LatencyReport {file_path} created ===")
        return file_path
