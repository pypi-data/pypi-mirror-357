"""
ApiChainer: A Python library for building declarative, chained HTTP request workflows.
"""

import asyncio
import logging
import re
import time
from copy import deepcopy
from typing import Any, Callable, Dict, List, Optional, Union

import aiofiles
import aiohttp
import requests

# ==============================================================================
# I. Custom Exceptions
# ==============================================================================


class ChainError(Exception):
    """Base exception for all library-specific errors."""

    pass


class RequestError(ChainError):
    """
    Raised when a request in the chain returns an HTTP error (4xx or 5xx).
    Contains the request and response objects for debugging.
    """

    def __init__(
        self, message: str, request_details: Dict, response: Optional[Union[requests.Response, aiohttp.ClientResponse]]
    ):
        super().__init__(message)
        self.request_details = request_details
        self.response = response

    def __str__(self) -> str:
        if self.response is None:
            return f"{super().__str__()} | No response object available."

        # Handle requests.Response
        if isinstance(self.response, requests.Response):
            status = self.response.status_code
            try:
                text = self.response.text
            except Exception:
                text = "N/A (failed to get text)"
        # Handle aiohttp.ClientResponse
        elif hasattr(self.response, "status"):
            status = self.response.status
            try:
                text = f"Async response with status {status}"
            except Exception:
                text = "N/A (failed to get text)"
        # Handle exceptions that might contain response info
        elif hasattr(self.response, "status") and hasattr(self.response, "message"):
            status = self.response.status
            text = str(self.response.message)
        else:
            # Fallback - try to extract useful info from any response-like object
            status = getattr(self.response, "status", getattr(self.response, "status_code", "Unknown"))
            text = getattr(self.response, "text", getattr(self.response, "message", str(self.response)))

        return f"{super().__str__()} | Status: {status} | Response Body: {text}"


class PlaceholderError(ChainError):
    """Raised on an error during placeholder formatting (e.g., invalid key or index)."""

    pass


class PollingTimeoutError(ChainError):
    """Raised by the poll() method if the condition is not met within the specified timeout."""

    pass


# ==============================================================================
# II. Internal Helper for Placeholder Resolution
# ==============================================================================


class _ValueExtractor:
    """A helper class to safely extract values from results and context based on a path string."""

    def __init__(self, results: List[Dict], context: Dict):
        self._results = results
        self._context = context
        self._step_regex = re.compile(r"step\[(\d+)\]")
        self._safe_placeholder_pattern = re.compile(r"^(prev|ctx|step\[\d+\])(\.[a-zA-Z_][a-zA-Z0-9_]*)*$")

    def get_value(self, path: str) -> Any:
        if not path:
            raise PlaceholderError("Placeholder path cannot be empty.")

        if not self._safe_placeholder_pattern.match(path):
            raise PlaceholderError(
                f"Invalid placeholder syntax: '{path}'. Must match pattern 'prev|ctx|step[N]' followed by optional dot-separated properties."
            )

        try:
            base_key, _, remainder = path.partition(".")
            target_obj = self._get_base_object(base_key)
            if not remainder:
                return target_obj
            return self._traverse_path(target_obj, remainder)
        except (KeyError, IndexError, AttributeError, TypeError) as e:
            raise PlaceholderError(f"Failed to resolve placeholder '{path}': {e}") from e

    def _get_base_object(self, base_key: str) -> Any:
        if base_key == "prev":
            if not self._results:
                raise PlaceholderError("Cannot use '{prev...}' placeholder as no previous steps have been run.")
            return self._results[-1]
        if base_key == "ctx":
            return self._context
        match = self._step_regex.match(base_key)
        if match:
            idx = int(match.group(1))
            if idx >= len(self._results):
                raise PlaceholderError(
                    f"Cannot access step[{idx}]: index out of range. Only {len(self._results)} steps have run."
                )
            return self._results[idx]
        raise PlaceholderError(f"Invalid placeholder root: must be 'prev', 'ctx', or 'step[N]', but got '{base_key}'.")

    @staticmethod
    def _traverse_path(obj: Any, path_str: str) -> Any:
        for part in path_str.split("."):
            if isinstance(obj, dict):
                obj = obj[part]
            else:
                obj = getattr(obj, part)
        return obj


# ==============================================================================
# III. Base Chain Class
# ==============================================================================


class _BaseChain:
    """
    Provides the core fluent interface and state management for both sync and async chains.
    This class is not intended for direct instantiation.
    """

    def __init__(
        self,
        base_url: str = "",
        initial_context: Optional[Dict] = None,
        on_before_step: Optional[Callable[[Dict], None]] = None,
        on_after_step: Optional[Callable[[Dict], None]] = None,
        on_error: Optional[Callable[[RequestError], None]] = None,
        enable_logging: bool = False,
    ):
        self._base_url = base_url
        self._initial_context = initial_context or {}
        self._steps: List[Dict] = []
        self._results: List[Dict] = []
        self._headers: Dict[str, str] = {}
        self._on_before_step = on_before_step
        self._on_after_step = on_after_step
        self._on_error = on_error
        self._logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}") if enable_logging else None

    def _add_step(self, step_type: str, **kwargs):
        self._steps.append({"type": step_type, **kwargs})

    def _resolve_placeholders(self, data: Any) -> Any:
        extractor = _ValueExtractor(self._results, self._initial_context)

        def replacer(match):
            path = match.group(1).strip()
            return str(extractor.get_value(path))

        if isinstance(data, str):
            return re.sub(r"\{(.*?)\}", replacer, data)
        if isinstance(data, dict):
            return {self._resolve_placeholders(k): self._resolve_placeholders(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self._resolve_placeholders(item) for item in data]
        return data

    def _validate_url(self, url: str) -> None:
        """Validate URL format and security."""
        if not url or not isinstance(url, str):
            raise ChainError("URL must be a non-empty string")

        # Allow relative URLs and absolute URLs with http/https
        if not (url.startswith("/") or url.startswith(("http://", "https://")) or "{" in url):
            raise ChainError("URL must be absolute (http/https), relative (/path), or contain placeholders")

    def _full_url(self, url: str, current_base_url: str) -> str:
        if url.startswith(("http://", "https://")):
            return url
        return f"{current_base_url.rstrip('/')}/{url.lstrip('/')}"

    def set_base_url(self, url: str) -> "_BaseChain":
        self._add_step("set_base_url", url=url)
        return self

    def set_header(self, key: str, value: str) -> "_BaseChain":
        self._add_step("set_header", key=key, value=value)
        return self

    def get(self, url: str, **kwargs) -> "_BaseChain":
        self._validate_url(url)
        self._add_step("request", method="GET", url=url, kwargs=kwargs)
        return self

    def post(self, url: str, **kwargs) -> "_BaseChain":
        self._add_step("request", method="POST", url=url, kwargs=kwargs)
        return self

    def put(self, url: str, **kwargs) -> "_BaseChain":
        self._add_step("request", method="PUT", url=url, kwargs=kwargs)
        return self

    def patch(self, url: str, **kwargs) -> "_BaseChain":
        self._add_step("request", method="PATCH", url=url, kwargs=kwargs)
        return self

    def delete(self, url: str, **kwargs) -> "_BaseChain":
        self._add_step("request", method="DELETE", url=url, kwargs=kwargs)
        return self

    def poll(self, url: str, until: Callable, interval_seconds: int = 10, timeout_seconds: int = 10) -> "_BaseChain":
        self._add_step("poll", url=url, until=until, interval=interval_seconds, timeout=timeout_seconds)
        return self

    def upload_file(self, url: str, filepath: str, field_name: str = "file", **kwargs) -> "_BaseChain":
        self._add_step("upload", url=url, filepath=filepath, field_name=field_name, kwargs=kwargs)
        return self

    def retry_on_failure(self, attempts: int = 3, delay_seconds: float = 1) -> "_BaseChain":
        if not self._steps or self._steps[-1].get("type") not in ("request", "upload"):
            raise ChainError("retry_on_failure() can only be applied immediately after a request or upload step.")
        self._steps[-1]["retry"] = {"attempts": attempts, "delay": delay_seconds}
        return self


# ==============================================================================
# IV. Synchronous Client
# ==============================================================================


class ApiChain(_BaseChain):
    """
    Builds and executes a chain of HTTP requests synchronously using 'requests'.
    """

    def _store_result(self, response: requests.Response):
        try:
            json_content = response.json()
        except requests.exceptions.JSONDecodeError:
            json_content = None
        result_dict = {
            "json": json_content,
            "text": response.text,
            "headers": response.headers,
            "status_code": response.status_code,
            "ok": response.ok,
            "content": response.content,
        }
        self._results.append(result_dict)
        if self._on_after_step:
            self._on_after_step(deepcopy(result_dict))

    def _execute_request_step(
        self, resolved_step: Dict, session: requests.Session, current_base_url: str
    ) -> requests.Response:
        """Execute a single request or upload step with retry logic."""
        retry_config = resolved_step.get("retry", {"attempts": 1, "delay": 0})
        step_type = resolved_step.get("type")

        for attempt in range(retry_config["attempts"]):
            try:
                url = self._full_url(resolved_step["url"], current_base_url)

                # Perform the request
                if step_type == "request":
                    response = session.request(resolved_step["method"], url, **resolved_step.get("kwargs", {}))
                elif step_type == "upload":
                    with open(resolved_step["filepath"], "rb") as f:
                        files = {resolved_step["field_name"]: f}
                        response = session.post(url, files=files, data=resolved_step.get("kwargs", {}).get("data"))
                else:
                    raise ChainError(f"Unknown step type: {step_type}")

                # Check for HTTP errors and raise our custom exception
                response.raise_for_status()
                return response

            except requests.exceptions.HTTPError as e:
                if attempt + 1 >= retry_config["attempts"]:
                    response_obj = getattr(e, "response", None)
                    req_err = RequestError(f"HTTP error after {attempt+1} attempts", resolved_step, response_obj)
                    if self._on_error:
                        self._on_error(req_err)
                    raise req_err from e
                time.sleep(retry_config["delay"])

            except requests.exceptions.RequestException as e:
                if attempt + 1 >= retry_config["attempts"]:
                    req_err = RequestError(f"Request failed after {attempt+1} attempts", resolved_step, None)
                    if self._on_error:
                        self._on_error(req_err)
                    raise req_err from e
                time.sleep(retry_config["delay"])

    def _execute_poll_step(self, resolved_step: Dict, session: requests.Session, current_base_url: str) -> requests.Response:
        """Execute a polling step."""
        start_time = time.monotonic()
        url = self._full_url(resolved_step["url"], current_base_url)

        while time.monotonic() - start_time < resolved_step["timeout"]:
            response = session.get(url)
            if resolved_step["until"](response):
                return response
            time.sleep(resolved_step["interval"])

        raise PollingTimeoutError(f"Polling timed out for URL: {url}")

    def run(self) -> requests.Response:
        """Execute the chain of requests synchronously."""
        self._results = []
        last_response: Optional[requests.Response] = None
        current_base_url = self._base_url

        with requests.Session() as session:
            session.headers.update(self._headers)

            for step in self._steps:
                if self._on_before_step:
                    self._on_before_step(deepcopy(step))

                resolved_step = self._resolve_placeholders(deepcopy(step))
                step_type = resolved_step.get("type")

                if step_type in ("request", "upload"):
                    # Add type back for _execute_request_step
                    resolved_step["type"] = step_type
                    last_response = self._execute_request_step(resolved_step, session, current_base_url)
                    self._store_result(last_response)

                elif step_type == "poll":
                    last_response = self._execute_poll_step(resolved_step, session, current_base_url)
                    self._store_result(last_response)

                elif step_type == "set_header":
                    session.headers[resolved_step["key"]] = resolved_step["value"]

                elif step_type == "set_base_url":
                    current_base_url = resolved_step["url"]

                else:
                    raise ChainError(f"Unknown step type: {step_type}")

        if last_response is None:
            raise ChainError("Chain executed but produced no response.")
        return last_response

    def run_and_save_to_file(self, filepath: str):
        response = self.run()
        with open(filepath, "wb") as f:
            f.write(response.content)


# ==============================================================================
# V. Asynchronous Client
# ==============================================================================


class AsyncApiChain(_BaseChain):
    """
    Builds and executes a chain of HTTP requests asynchronously using 'aiohttp'.
    """

    async def _store_result(self, response: aiohttp.ClientResponse):
        try:
            json_content = await response.json(content_type=None)
        except (ValueError, aiohttp.client_exceptions.ContentTypeError):
            json_content = None

        content = await response.read()
        text = content.decode("utf-8", errors="ignore")

        result_dict = {
            "json": json_content,
            "text": text,
            "headers": response.headers,
            "status_code": response.status,
            "ok": response.ok,
            "content": content,
        }
        self._results.append(result_dict)
        if self._on_after_step:
            self._on_after_step(deepcopy(result_dict))

    async def run_async(self) -> aiohttp.ClientResponse:
        self._results = []
        last_response: Optional[aiohttp.ClientResponse] = None
        current_base_url = self._base_url
        current_headers = self._headers.copy()

        async with aiohttp.ClientSession() as session:
            for step in self._steps:
                if self._on_before_step:
                    self._on_before_step(deepcopy(step))
                resolved_step = self._resolve_placeholders(deepcopy(step))
                step_type = resolved_step.pop("type")

                if step_type in ("request", "upload"):
                    retry_config = resolved_step.get("retry", {"attempts": 1, "delay": 0})
                    for attempt in range(retry_config["attempts"]):
                        try:
                            kwargs = resolved_step.get("kwargs", {})
                            kwargs["headers"] = {**current_headers, **kwargs.get("headers", {})}
                            url = self._full_url(resolved_step["url"], current_base_url)

                            async with session.request(resolved_step["method"], url, **kwargs) as response:
                                response.raise_for_status()
                                await self._store_result(response)
                                last_response = response
                                break

                        except aiohttp.ClientResponseError as e:
                            if attempt + 1 >= retry_config["attempts"]:
                                # Try to get the response from the exception, fall back to the exception itself
                                response_obj = getattr(e, "response", e)
                                req_err = RequestError(f"HTTP error after {attempt+1} attempts", resolved_step, response_obj)
                                if self._on_error:
                                    self._on_error(req_err)
                                raise req_err from e
                            await asyncio.sleep(retry_config["delay"])

                        except aiohttp.ClientError as e:
                            if attempt + 1 >= retry_config["attempts"]:
                                req_err = RequestError(f"Request failed after {attempt+1} attempts", resolved_step, None)
                                if self._on_error:
                                    self._on_error(req_err)
                                raise req_err from e
                            await asyncio.sleep(retry_config["delay"])

                elif step_type == "poll":
                    start_time = time.monotonic()
                    url = self._full_url(resolved_step["url"], current_base_url)
                    while time.monotonic() - start_time < resolved_step["timeout"]:
                        async with session.get(url, headers=current_headers) as response:
                            if resolved_step["until"](response):
                                await self._store_result(response)
                                last_response = response
                                break
                        await asyncio.sleep(resolved_step["interval"])
                    else:
                        raise PollingTimeoutError(f"Polling timed out for URL: {url}")
                elif step_type == "set_header":
                    current_headers[resolved_step["key"]] = resolved_step["value"]
                elif step_type == "set_base_url":
                    current_base_url = resolved_step["url"]

        if last_response is None:
            raise ChainError("Chain executed but produced no response.")
        return last_response

    async def run_and_save_to_file_async(self, filepath: str):
        response = await self.run_async()
        content = await response.read()
        async with aiofiles.open(filepath, mode="wb") as f:
            await f.write(content)
