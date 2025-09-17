#  HTTPXManager v1.0

### **Overview**

This release introduces **Pydantic integration**, **robust async HTTP requests**, and full **GET/POST/PUT/DELETE support** with retry and circuit breaker patterns. Logging and error handling have been significantly improved.

This version ensures type safety, fault-tolerance, and maintainable async code for your HTTP interactions.

---

## ✨ **New Features**

### 1. Pydantic Models

* `RequestPayload` model for request parameters:

  * `url`: `AnyHttpUrl` (validated URL)
  * `method`: `"GET" | "POST" | "PUT" | "DELETE"`
  * `body`, `headers`, `timeout`, `follow_redirects` optional
* `ResponsePayload` model added (future-ready for structured responses)

### 2. HTTPX Compatibility

* Automatic conversion of `AnyHttpUrl` to `str` for `httpx`.
* Fully supports **GET, POST, PUT, DELETE** methods with JSON payloads.

### 3. Retry & Circuit Breaker

* Integrated **Tenacity** retry decorator with `_should_retry` logic.
* Circuit breaker wraps `_execute_request` for fault-tolerance.
* Retry on network errors, timeouts, HTTP 5xx, and 429 rate limiting.

### 4. Structured Logging

* `Logger` dynamically reads log level from config.
* Detailed error logs including traceback.
* Warnings for invalid JSON responses.

### 5. Example Usage

* Working **GET** request example.
* Working **POST** request example with JSON body.

---

## 🐛 **Bug Fixes**

* Fixed `TypeError` when passing `AnyHttpUrl` to `httpx`.
* Fixed method signature mismatch when passing Pydantic payloads.
* Resolved logging and unexpected exception handling issues.

---

## ⚡ **Example Usage**

```python
import asyncio
from httpx_manager import HTTPXMANAGER, RequestPayload

async def main():
    http_manager = HTTPXMANAGER()

    # GET Example
    get_payload = RequestPayload(
        url="https://jsonplaceholder.typicode.com/posts/1",
        method="GET"
    )
    get_result = await http_manager.make_request(get_payload)
    print("GET result:", get_result)

    # POST Example
    post_payload = RequestPayload(
        url="https://jsonplaceholder.typicode.com/posts",
        method="POST",
        body={"title": "foo", "body": "bar", "userId": 1},
        headers={"Content-Type": "application/json"}
    )
    post_result = await http_manager.make_request(post_payload)
    print("POST result:", post_result)

asyncio.run(main())
```

---

## 🛠 **Configuration**

The manager reads from `config.HTTPXMANAGER_CONFIG`:

```python
HTTPXMANAGER_CONFIG = {
    "HTTPXMANAGER": "DEBUG",  # Logger level
    "TIMEOUT": 10,  # Request timeout in seconds
    "CIRCUIT_FAILURE_THRESHOLD": 5,
    "CIRCUIT_RECOVERY_TIMEOUT": 30,
    "RETRY_ATTEMPTS": 3,
    "RETRY_MULTIPLIER": 1,
    "RETRY_MIN_WAIT": 1,
    "RETRY_MAX_WAIT": 10,
}
```

* **Timeouts** and **retry/backoff** fully configurable.
* Circuit breaker prevents repeated failures from overwhelming the service.

---

## 📦 **Requirements**

* Python ≥ 3.10
* `httpx`, `tenacity`, `pydantic`, `aiocircuitbreaker`
* Optional: custom `Logger` class for structured logging
uv add httpx>=0.28.1 tenacity>=9.1.2 aiocircuitbreaker>=2.0.0
---

## 📄 **License**

MIT License – free to use and modify.


