# from datetime import datetime, timedelta, timezone

# from slowking.adapters.report import LatencyReport
# from slowking.domain import model


# def test_latency_report_create():
#     # TODO how to test output?
#     # TODO how to override config (output dir, filename)
#     doc = model.Document(
#         name="test doc",
#         file_path="test path",
#     )
#     doc.upload_time_start = datetime.now(timezone.utc) - timedelta(seconds=5)
#     doc.upload_time_end = datetime.now(timezone.utc)
#     doc2 = model.Document(
#         name="test doc2",
#         file_path="test path",
#     )
#     doc2.upload_time_start = datetime.now(timezone.utc) - timedelta(seconds=2)
#     doc2.upload_time_end = datetime.now(timezone.utc)

#     benchmark = model.Benchmark(
#         name="test bm",
#         benchmark_type="latency",
#         eigen_platform_version="5.11.0-rc.1",
#         target_infra="k8s",
#         target_url="localhost",
#         username="test user",
#         password="test pw",
#         project=model.Project(name="test project", document=[doc, doc2]),
#     )
#     LatencyReport.create(benchmark)
