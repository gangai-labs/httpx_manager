# HTTPXMANAGER

HTTPXMANAGER is a robust async HTTP request helper with built-in retry and circuit breaker patterns. It provides a reliable way to make HTTP requests while handling failures gracefully.

## Installation

To install HTTPXMANAGER, use the following command:

```bash
uv add httpx>=0.28.1 tenacity>=9.1.2 aiocircuitbreaker>=2.0.0

Usage
Importing HTTPXMANAGER

First, import HTTPXMANAGER in your Python script:

from httpx_manager import HTTPXMANAGER

Making a Request

You can make a GET request as follows:

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

Making a POST Request

You can also make a POST request:

async def example_usage():
    http_manager = HTTPXMANAGER()

    try:
        result = await http_manager.make_request(
            "https://api.example.com/data",
            method="POST",
            body={"key": "value"},
            headers={"Authorization": "Bearer token"}
        )

        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Success: {result}")

    except Exception as e:
        print(f"All retries failed: {e}")

Configuration

HTTPXMANAGER can be configured using a configuration file. Here is an example configuration:

{
  "HTTPXMANAGER": {
    "LOGGING_LEVEL": "DEBUG",
    "TIMEOUT": 10,
    "CIRCUIT_FAILURE_THRESHOLD": 5,
    "CIRCUIT_RECOVERY_TIMEOUT": 30,
    "RETRY_ATTEMPTS": 3,
    "RETRY_MULTIPLIER": 1,
    "RETRY_MIN_WAIT": 1,
    "RETRY_MAX_WAIT": 10
  }
}

Error Handling

HTTPXMANAGER includes built-in error handling for common HTTP errors and network issues. It also supports circuit breaker patterns to prevent overloading of services.
Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.
License

This project is licensed under the MIT License.
 
