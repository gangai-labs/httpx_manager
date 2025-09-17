import json
from typing import Optional, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import HTTPXMANAGER_CONFIG
from src.helpers.logger import Logger
from aiocircuitbreaker import CircuitBreaker, CircuitBreakerError


def _should_retry(exception: Exception) -> bool:
    """Determine if a request should be retried based on exception type."""
    if isinstance(exception, (httpx.TimeoutException, httpx.NetworkError, CircuitBreakerError)):
        return True
    if isinstance(exception, httpx.HTTPStatusError):
        # Retry on server errors (5xx) and rate limiting (429)
        return exception.response.status_code >= 500 or exception.response.status_code == 429
    return False


class HTTPXMANAGER:
    def __init__(self):
        self.logger = Logger().create_logger(logging_level=HTTPXMANAGER_CONFIG[__class__.__name__])
        self.timeout = HTTPXMANAGER_CONFIG['TIMEOUT']

        # Circuit breaker configuration
        self.circuit_failure_threshold = HTTPXMANAGER_CONFIG.get('CIRCUIT_FAILURE_THRESHOLD', 5)
        self.circuit_recovery_timeout = HTTPXMANAGER_CONFIG.get('CIRCUIT_RECOVERY_TIMEOUT', 30)

        # Retry configuration
        self.retry_attempts = HTTPXMANAGER_CONFIG.get('RETRY_ATTEMPTS', 3)
        self.retry_multiplier = HTTPXMANAGER_CONFIG.get('RETRY_MULTIPLIER', 1)
        self.retry_min_wait = HTTPXMANAGER_CONFIG.get('RETRY_MIN_WAIT', 1)
        self.retry_max_wait = HTTPXMANAGER_CONFIG.get('RETRY_MAX_WAIT', 10)

        # Initialize circuit breaker with your custom class
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.circuit_failure_threshold,
            recovery_timeout=self.circuit_recovery_timeout,
            expected_exception=(httpx.TimeoutException, httpx.RequestError, httpx.HTTPStatusError),
            name="HTTPXManagerCircuitBreaker"
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(
            lambda e: isinstance(e, (httpx.TimeoutException, httpx.NetworkError, CircuitBreakerError)) or
                      (isinstance(e, httpx.HTTPStatusError) and (
                              e.response.status_code >= 500 or e.response.status_code == 429))),
        reraise=True
    )
    async def make_request(self, url: str, method: str = "GET", body: Optional[dict] = None,
                           headers: Optional[dict] = None, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Robust HTTP request helper with retry and circuit breaker patterns."""

        # Use circuit breaker to wrap the actual request call
        try:
            # Since your CircuitBreaker class is a decorator, we need to use it differently
            # Create a decorated version of _execute_request
            decorated_execute = self.circuit_breaker.decorate(self._execute_request)
            return await decorated_execute(url, method, body, headers, timeout)
        except CircuitBreakerError as e:
            self.logger.warning(f"Circuit breaker open: {url} - {e}")
            return {"error": {"code": "CIRCUIT_BREAKER_OPEN", "message": "Service temporarily unavailable"}}
        except Exception as e:
            # This will be caught by the retry decorator for retry-able exceptions
            raise

    async def _execute_request(self, url: str, method: str, body: Optional[dict],
                               headers: Optional[dict], timeout: Optional[float]) -> Dict[str, Any]:
        """Actual HTTP request execution."""
        self.logger.debug(f"Making {method} request to {url}")
        self.logger.debug(f"Request body: {body}")

        timeout = timeout or self.timeout
        headers = headers or {"Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method.upper() == "GET":
                    self.logger.debug("Sending GET request")
                    resp = await client.get(url, headers=headers)
                elif method.upper() == "POST":
                    self.logger.debug("Sending POST request")
                    resp = await client.post(url, json=body, headers=headers)
                elif method.upper() == "PUT":
                    self.logger.debug("Sending PUT request")
                    resp = await client.put(url, json=body, headers=headers)
                elif method.upper() == "DELETE":
                    self.logger.debug("Sending DELETE request")
                    resp = await client.delete(url, headers=headers)
                else:
                    error_msg = f"Unsupported HTTP method: {method}"
                    self.logger.error(error_msg)
                    return {"error": {"code": "INVALID_METHOD", "message": error_msg}}

                # Raise exception for HTTP error status codes
                resp.raise_for_status()

                self.logger.debug(f"Response status: {resp.status_code}")
                try:
                    response_json = resp.json()
                    self.logger.debug(f"Response JSON: {response_json}")
                    return response_json
                except json.JSONDecodeError:
                    text = resp.text
                    self.logger.warning(f"Response is not valid JSON: {text[:200]}")
                    return {"text": text, "status_code": resp.status_code}

        except httpx.TimeoutException as e:
            self.logger.error(f"Request timeout: {url}")
            self.logger.exception(e)
            raise
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error {e.response.status_code}: {url}")
            self.logger.exception(e)
            raise
        except httpx.RequestError as e:
            self.logger.error(f"Request failed: {url}")
            self.logger.exception(e)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in _execute_request: {url}")
            self.logger.exception(e)
            return {"error": {"code": "UNEXPECTED_ERROR", "message": f"Unexpected error: {e}"}}





if __name__ == '__main__':
    # Usage example
    async def example_usage():
        http_manager = HTTPXMANAGER()

        try:
            result = await http_manager.make_request(
                "https://api.example.com/data",
                method="GET",
                headers={"Authorization": "Bearer token"}
            )

            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Success: {result}")

        except Exception as e:
            print(f"All retries failed: {e}")