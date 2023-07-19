"""
Notification adapters. Small examples for logging and email but
could be extended to send different emails or Slack messages, etc.
"""
import abc
import logging.config
import smtplib

from slowking.config import settings
from slowking.domain import model

logger = logging.getLogger(__name__)


class AbstractNotifications(abc.ABC):
    @abc.abstractmethod
    def send(self, benchmark: model.Benchmark, message: str):
        raise NotImplementedError


class LogNotifications(AbstractNotifications):
    def send(self, benchmark: model.Benchmark, message: str):
        logger.info(f"Sending notification for benchmark {benchmark.name}")


class EmailNotifications(AbstractNotifications):
    def __init__(self, smtp_host=settings.EMAIL_HOST, port=settings.EMAIL_PORT):
        self.server = smtplib.SMTP(smtp_host, port=port)
        self.server.noop()

    def send(self, benchmark: model.Benchmark, message: str) -> None:
        subject = f"Benchmark Report: {benchmark.name}"
        body = f"Report generated: {message}"
        msg = f"Subject: {subject}\n{body}"

        # Hard coded as an example, could be taken from the benchmark aggregate
        # the CreateBenchmark command could have an email field
        destination = ["hello@example.com"]

        self.server.sendmail(
            from_addr="benchmarks@slowking.com",
            to_addrs=destination,
            msg=msg,
        )
