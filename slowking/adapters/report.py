"""
Report generation adapters.
"""
import csv
import datetime

from slowking.domain import model

# TODO move to config, switch to docker path
# OUTPUT_DIR = "/home/app/reports"
OUTPUT_DIR = "./reports/"
OUTPUT_FILENAME = "report.csv"


def create_report(benchmark: model.Benchmark):
    """
    Create report for given benchmark.
    """
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
    print(f"=== create_report :: fields === : {fields}")
    with open(f"{OUTPUT_DIR}{OUTPUT_FILENAME}", "w") as csv_file:
        # TODO these are the headers e.g. "benchmark name", "doc name", "upload time"
        fieldnames = [
            "Benchmark Name",
            "Benchmark Type",
            "Infra",
            "Eigen Version",
            "Doc Name",
            "Upload Time (seconds)",
        ]

        csv_writer = csv.DictWriter(
            csv_file, delimiter=",", quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames
        )
        csv_writer.writeheader()
        for field in fields:
            csv_writer.writerow(field)


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
    create_report(benchmark)
