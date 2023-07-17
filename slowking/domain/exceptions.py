"""
Domain custom exceptions
"""


class MessageNotAssignedToBenchmarkError(Exception):
    """
    If the Message [Command | Event] is not assigned to the Benchmark
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
