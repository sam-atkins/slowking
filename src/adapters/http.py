"""
HTTP client adapter to communicate with the benchmark target instance.

This uses some of the Bird client code as a starting point. Copy/paste to aid logging
and dev, and to only bring in the functionality I need. In 'real life' would probably
install and use ECU.
"""
from __future__ import annotations

import logging.config
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Optional
from urllib.parse import urljoin

from requests import HTTPError, Response, Session
from tenacity import retry, stop_after_attempt, wait_fixed, wait_random

logger = logging.getLogger(__name__)


AUTH_RETRIES = 5


class HttpClient(Session):
    """Class for interacting with the Eigen application's REST API."""

    EXPIRED_TOKEN_DETAIL = "Token has expired."

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        base_auth_url: str = "",
        eigen_version: str = "",
        conn_id: str = "",
        verify: bool = False,
    ) -> None:
        """Initialize the client.

        Args:
            base_url (str): base url to construct url with. Should have format:
                `<schema><host>:<port>/` or `<schema><host>/` where <schema>
                is http:// or https://, <host> is a domain or IP address and
                <port> is a number.
            base_auth_url (str): an optional base auth url to construct url to
                authenticate against. Should have the same format as the `base_url`.
                If this is left out then the `base_url` will be used to authenticate.
            username (str): user with access to Eigen application.
            password (str): password for above user.
            eigen_version (str): Specify the version of Eigen application that the
                consumer is using. Can be  used in order to modify behaviour in the
                end user. If not given, assumed to be the latest.
            conn_id (str): Optional human readable identifier of connection.
            verify (bool): Whether to verify requests.
        """
        super().__init__()

        # Store the credentials so we can use them for re-authentication
        self.username = username
        self.password = password
        self.conn_id = conn_id or base_url

        if not base_url.endswith("/"):
            base_url += "/"

        if not base_auth_url:
            base_auth_url = base_url

        if not base_auth_url.endswith("/"):
            base_auth_url += "/"

        self.base_url = base_url
        self.base_url_v1 = f"{base_url}api/v1/"
        self.base_url_v2 = f"{base_url}api/v2/"
        self.base_url_project_management_v2 = f"{base_url}api/project_management/v2/"
        self.auth_url = f"{base_auth_url}auth/v1/token/"
        self.base_url_training_v1 = f"{base_url}api/training_input/v1/"
        self.base_url_prediction_v1 = f"{base_url}api/prediction/v1/"
        self.token = None
        self._csrf_token = None

        self.verify = verify

        # Eigen version intended to
        self.eigen_version = eigen_version

        self._get_auth_token()

    @staticmethod
    def _raise_for_status(
        response: Response, expected_code: Optional[int] = None, info: Any = None
    ) -> None:
        """Extend the requests library `raise_for_status`.

        Args:
            response: `requests.Response` object
            expected_code: If a specific code was expected, what
                it was.  Otherwise, any error status code will error up
            info: Any stringifiable object for additional info to print

        Raises:
            HTTPError: when there is an error to raise
        """
        error_type = ""
        if isinstance(response.reason, bytes):
            try:
                reason = response.reason.decode("utf-8")
            except UnicodeDecodeError:
                reason = response.reason.decode("iso-8859-1")
        else:
            reason = response.reason

        if 400 <= response.status_code < 500:
            error_type = "Client Error"
        elif 500 <= response.status_code < 600:
            error_type = "Server Error"
        elif expected_code and response.status_code != expected_code:
            error_type = "Unexpected Status"

        if error_type:
            http_error_msg = (
                f"{response.status_code} {error_type}: "
                f"{reason} for url: {response.url}\n\n"
                f"Response Text: {str(response.text)}"
            )

            if info:
                http_error_msg += f"\n\nAdditional Information: {info}"
            raise HTTPError(http_error_msg, response=response)

    @retry(
        wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(AUTH_RETRIES)
    )
    def request(self, method: str, url: str, **kwargs) -> Response:
        """Override the base Session.request.

        Adds re-authentication logic to the `request` method.

        Args:
            method: the method of the request, eg. "GET"
            url: the url for the request
            **kwargs: any other keyword arguments

        Raises:
            AuthRetriesExceededException: when the retry limit has been reached for
                re-authentication
            HTTPError: when an HTTPError is raised and token is valid

        Returns:
            a `requests` `Response` object
        """
        # retry_attempts = 0

        # TODO replace with tenacity
        # while retry_attempts <= AUTH_RETRIES:
        #     try:
        #         response = super().request(method, url, **kwargs)
        #         self._raise_for_status(response)

        #         if response.headers.get("Deprecation"):
        #             logger.warning("The url '%s' is deprecated", url)

        #         return response
        #     except HTTPError as exc:
        #         if self._is_token_expiry(exc) is False:
        #             raise exc
        #         logger.info("Token expired, attempting to reauthenticate")

        #         self._refresh_auth()

        #         logger.info("New authentication token created - reattempting request")

        #     retry_attempts += 1

        try:
            response = super().request(method, url, **kwargs)
            self._raise_for_status(response)

            if response.headers.get("Deprecation"):
                logger.warning("The url '%s' is deprecated", url)

            return response
        except HTTPError as exc:
            if self._is_token_expiry(exc) is False:
                raise exc
            logger.info("Token expired, attempting to reauthenticate")

            self._refresh_auth()

            logger.info("New authentication token created - reattempting request")

        raise AuthRetriesExceededException(
            f"Auth token has expired and retries exceeded for url: {url}"
            # f"retries count: {retry_attempts} - retry limit: {AUTH_RETRIES}"
        )

    def _refresh_auth(self) -> None:
        """Add the auth header.

        Separating this from get_auth_token makes it easier for us to override refresh
        behaviour in a child class
        """
        self._get_auth_token()

    def _get_auth_token(
        self, username: Optional[str] = None, password: Optional[str] = None
    ) -> None:
        """Retrieve an Eigen auth token.

        Args:
            username: an optional username to authenticate against (defaults to the
                `username` instance variable)
            password: an optional password to authenticate against (defaults to the
                `password` instance variable)
        """
        username = username or self.username
        password = password or self.password

        # Token will be stored in the session's cookiejar
        response = self.post(
            url=self.auth_url, json={"username": username, "password": password}
        )
        self._raise_for_status(response)

        # Reset the csrf_token so it will be reinitialised by the property if used
        self._csrf_token = None

    def _is_token_expiry(self, error: HTTPError) -> bool:
        """Check whether response error is a token expiry error.

        Args:
            error: the error to check

        Returns:
            a bool to indicate whether the error is a token expiry error
        """
        if error.response.status_code != 401:
            return False

        try:
            error_detail = error.response.json()["error"]["detail"]
        except KeyError:
            return False

        if error_detail != self.EXPIRED_TOKEN_DETAIL:
            return False

        return True

    @property
    def csrf_token(self) -> str:
        """Return the csrf_token.

        Returns:
            the `csrf_token`
        """
        if self._csrf_token is None:
            url = f"{self.base_url_v2}api-csrf-token/"
            res = self.get(url=url)
            self._raise_for_status(res)
            self._csrf_token = res.json()["csrf_token"]

        return self._csrf_token

    def create_project(self, name: str, description: str) -> dict[str, Any]:
        url = urljoin(self.base_url_project_management_v2, "projects")
        res = self.post(url, json={"name": name, "description": description})
        self._raise_for_status(res)
        res_json = res.json()
        logger.info(f"=== Client :: Create project response {res}")
        return res_json

    # TODO document uploader - use this or update by copying from ECU?
    def upload_files(
        self, eigen_document_type_id: str, files: list[BirdDocument]
    ) -> list[dict[str, Any]]:
        """Upload files.

        Args:
            eigen_document_type_id: the `document_type_id`
            files: a list of files to upload

        Returns:
            the response from Eigen
        """
        return self.upload_files_v3_which_is_actually_at_v1(
            eigen_document_type_id, files
        )

    def upload_files_v3_which_is_actually_at_v1(
        self, eigen_document_type_id: str, files: list[BirdDocument]
    ) -> list[dict[str, Any]]:
        """Upload files.

        Args:
            eigen_document_type_id: the `document_type_id`
            files: a list of files to upload

        Returns:
            the response from Eigen
        """
        url = f"{self.base_url_v1}document_uploader/"
        res = self.post(
            url=url,
            data={"document_type_id": eigen_document_type_id},
            files=[("files", (f.filename, f.data)) for f in files],
            headers={
                "X-CSRFToken": self.csrf_token,
                "Referer": f"{self.base_url_v2}api-csrf-token/",
            },
            cookies={"csrftoken": self.csrf_token},
        )
        self._raise_for_status(res)
        return res.json()


@dataclass
class BirdDocument:
    """Wrapper for file objects used by the Bird class to upload files."""

    filename: str
    data: BytesIO


class BaseError(Exception):
    """Base error."""

    def __init__(self, msg):
        """Initialise the error."""
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        """Return the str."""
        return f"{self.msg}"

    def __repr__(self):
        """Return the representation."""
        return f"{self.__name__}({self.msg})"  # type: ignore


class EigenError(BaseError):
    """Generic Eigen error."""


class AuthRetriesExceededException(BaseError):
    """Raised when max auth retries has been exceeded."""
