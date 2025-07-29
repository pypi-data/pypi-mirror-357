# ApiChainer

[![Tests](https://github.com/No0key/apichainer/workflows/Run%20Tests/badge.svg)](https://github.com/No0key/apichainer/actions)
[![PyPI version](https://badge.fury.io/py/apichainer.svg)](https://badge.fury.io/py/apichainer)
[![Python versions](https://img.shields.io/pypi/pyversions/apichainer.svg)](https://pypi.org/project/apichainer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ApiChainer is a declarative Python library for building chained HTTP requests using a fluent interface. 
It allows you to describe complex, multi-step API workflows, passing data between requests without writing a lot of boilerplate code.

The library provides both synchronous (`ApiChain`) and asynchronous (`AsyncApiChain`) clients, built on top of `requests` and `aiohttp` respectively.

## Key Features
- **Fluent Interface**: Create sequences of requests with methods like `.get()`, `.post()`, `.put()`, `.patch()`, `.delete()`.

- **Data Forwarding (Placeholders)**: Easily use data from a previous step's response in subsequent requests (`{prev.json.id}`, `{prev.text}`, `{prev.headers}`).

- **Centralized Context**: Define initial data (`{ctx.user_id}`) that is accessible in any step.

- **Advanced Placeholders**: Access specific steps with `{step[0].json}` or `{step[1].text}` syntax.

- **File Operations**: Upload files with `.upload_file()` and save responses to files.

- **Macros**: Use high-level methods for complex operations like polling (`.poll()`) or retrying on failure (`.retry_on_failure()`).

- **Synchronous & Asynchronous Modes**: Full support for both traditional scripts (`requests`) and async frameworks like FastAPI (`aiohttp`).

- **Callbacks**: Inject logging or monitoring logic with `on_before_step`, `on_after_step`, and `on_error` callbacks.

- **Granular Error Handling**: Clear exceptions for debugging issues with requests, placeholders, polling timeouts, or general chain errors.

- **Security**: Built-in URL validation and safe placeholder processing.

- **Logging Support**: Optional logging for debugging with `enable_logging=True`.

## Installation

**Requirements:** Python 3.9+

```bash
pip install apichainer
```

For development:
```bash
poetry install
```

## Quick Start

### Synchronous Example
Let's say we need to log in, get a token, and then use that token to request user data.

```python
from apichainer import ApiChain, RequestError

BASE_URL = "https://api.example.com"

try:
    # 1. POST /login to get a token
    # 2. GET /me using the token from step 1
    chain = (
        ApiChain(base_url=BASE_URL)
        .post("/login", json={"username": "admin", "password": "password123"})
        .set_header("Authorization", "Bearer {prev.json.token}")
        .get("/me")
    )

    response = chain.run()
    
    print("User data:", response.json())

except RequestError as e:
    print(f"Chain execution failed: {e}")
    print(f"Status code: {e.response.status_code}")
```

### Asynchronous Example with FastAPI

The same workflow, but in an asynchronous context.

```python
# main.py (in your FastAPI application)
from fastapi import FastAPI
from apichainer import AsyncApiChain

app = FastAPI()
BASE_URL = "https://api.internal.service"

@app.get("/process-user/{user_id}")
async def process_user(user_id: int):
    # Context to pass static data into the chain
    context = {"user_id": user_id}
    
    # 1. Get task information for the user
    # 2. Post the result to another endpoint
    chain = (
        AsyncApiChain(base_url=BASE_URL, initial_context=context)
        .get("/tasks/{ctx.user_id}")
        .post("/results", json={
            "userId": "{ctx.user_id}",
            "taskData": "{prev.json}"
        })
    )

    response = await chain.run_async()
    
    return {"status": response.status, "response_text": await response.text()}
```

## Advanced Features

### File Upload
```python
from apichainer import ApiChain

chain = (
    ApiChain(base_url="https://api.example.com")
    .post("/login", json={"username": "user", "password": "pass"})
    .upload_file("/files", "/path/to/file.pdf", field_name="document")
    .retry_on_failure(attempts=3, delay_seconds=2)
)

response = chain.run()
```

### Polling Operations
```python
from apichainer import ApiChain

def is_ready(response):
    return response.json().get("status") == "completed"

chain = (
    ApiChain(base_url="https://api.example.com")
    .post("/jobs", json={"type": "export"})
    .poll("/jobs/{prev.json.job_id}", until=is_ready, interval_seconds=5, timeout_seconds=120)
)

response = chain.run()
```

### Advanced Placeholders
```python
from apichainer import ApiChain

chain = (
    ApiChain(base_url="https://api.example.com", initial_context={"user_id": 123})
    .get("/users/{ctx.user_id}")  # Context placeholder
    .get("/posts/{prev.json.id}")  # Previous step JSON
    .get("/comments?status_code={prev.status_code}")  # Previous step status
    .get("/metadata?step0_text={step[0].text}")  # Specific step access
)

response = chain.run()
```

### Callbacks and Logging
```python
from apichainer import ApiChain

def before_step(step_data):
    print(f"Executing: {step_data}")

def after_step(result):
    print(f"Result: {result['status_code']}")

def on_error(error):
    print(f"Error occurred: {error}")

chain = (
    ApiChain(
        base_url="https://api.example.com",
        on_before_step=before_step,
        on_after_step=after_step,
        on_error=on_error,
        enable_logging=True
    )
    .get("/data")
)

response = chain.run()
```

### Save Response to File
```python
from apichainer import ApiChain, AsyncApiChain

# Synchronous
chain = ApiChain(base_url="https://api.example.com").get("/download")
chain.run_and_save_to_file("output.pdf")

# Asynchronous
async_chain = AsyncApiChain(base_url="https://api.example.com").get("/download")
await async_chain.run_and_save_to_file_async("output.pdf")
```

## Exception Handling

ApiChainer provides specific exceptions for different error scenarios:

```python
from apichainer import (
    ApiChain, 
    RequestError,      # HTTP request errors
    PlaceholderError,  # Placeholder resolution errors  
    ChainError,        # General chain execution errors
    PollingTimeoutError # Polling timeout errors
)

try:
    response = ApiChain(base_url="https://api.example.com").get("/data").run()
except RequestError as e:
    print(f"HTTP error: {e}")
    print(f"Response: {e.response}")
except PlaceholderError as e:
    print(f"Placeholder error: {e}")
except PollingTimeoutError as e:
    print(f"Polling timeout: {e}")
except ChainError as e:
    print(f"Chain error: {e}")
```

# Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

# License
This project is licensed under the MIT License - see the LICENSE file for details.
