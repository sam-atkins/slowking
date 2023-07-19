"""
Domain custom exceptions
"""


class InvalidBenchmarkTypeError(Exception):
    """
    Benchmark Type is not valid
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class MessageNotAssignedToBenchmarkError(Exception):
    """
    Message [Command | Event] is not assigned to the Benchmark
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
