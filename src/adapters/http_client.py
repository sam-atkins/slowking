"""
HTTP client adapter to communicate with the benchmark target instance.

For retries: https://tenacity.readthedocs.io/en/latest/
@retry(wait=wait_fixed(3) + wait_random(0, 2))
@retry(stop=(stop_after_delay(10) | stop_after_attempt(5)))
combine some variation of the 2 above
"""


class HttpClient:
    pass
