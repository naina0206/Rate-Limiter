# Redis-Based Rate Limiter using Django

A production-inspired rate limiter built with **Django**, **Redis**, and **Django REST Framework**. This project demonstrates how different rate-limiting algorithms can be implemented using Redis while keeping the architecture modular and extensible.

---

## Features

* Fixed Window Rate Limiting
* Sliding Window Rate Limiting
* Redis as the storage backend
* Middleware-based request interception
* Factory Pattern for algorithm selection
* Custom exception handling
* Configurable rate limits through `settings.py`
* REST API for testing

---

## Tech Stack

* Python
* Django
* Django REST Framework
* Redis
* Docker

---


# How It Works

Every incoming request passes through a custom Django middleware before reaching the API.

The middleware:

1. Identifies the client IP.
2. Generates a Redis key.
3. Retrieves the configured rate limiter.
4. Checks whether the request should be allowed.
5. Returns **HTTP 429 (Too Many Requests)** if the limit has been exceeded.

---

# Supported Algorithms

## 1. Fixed Window

The Fixed Window algorithm stores a simple counter in Redis for each client.

For every request:

* Retrieve the current request count.
* Create the key if it does not exist.
* Increment the counter.
* Reject the request if the counter exceeds the configured limit.
* Let Redis automatically delete the key after the configured window expires.

### Redis Commands Used

* `GET`
* `SET`
* `INCR`
* `EXPIRE`

### Advantages

* Very simple
* Fast
* Low memory usage

### Limitation

Requests can burst near the boundary of two consecutive windows.

---

## 2. Sliding Window

The Sliding Window algorithm stores request timestamps inside a Redis Sorted Set.

For every request:

* Remove timestamps outside the current window.
* Count the remaining requests.
* Reject the request if the limit has already been reached.
* Store the current request timestamp.
* Refresh the expiration time.

### Redis Commands Used

* `ZREMRANGEBYSCORE`
* `ZCARD`
* `ZADD`
* `EXPIRE`

### Advantages

* Eliminates the boundary problem of the Fixed Window algorithm.
* Provides smoother and more accurate rate limiting.

### Trade-offs

* Slightly higher memory usage.
* More Redis operations per request.

---

# Selecting the Algorithm

The active rate-limiting algorithm can be selected from `settings.py`.

```python
RATE_LIMIT = 5
RATE_LIMIT_WINDOW = 60

RATE_LIMIT_ALGORITHM = "fixed"
```

or

```python
RATE_LIMIT_ALGORITHM = "sliding"
```

The middleware remains unchanged because the appropriate implementation is selected through a factory.

---
# Architecture Diagram
```mermaid
flowchart LR

    Client["Client (Browser / Postman)"]

    subgraph Django
        MW["RateLimiterMiddleware"]
        Factory["RateLimiterFactory"]
        Fixed["FixedWindowRateLimiter"]
        Sliding["SlidingWindowRateLimiter"]
        View["DRF View"]
    end

    subgraph Redis
        Redis[(Redis)]
    end

    Client --> MW

    MW --> Factory

    Factory --> Fixed
    Factory --> Sliding

    Fixed --> Redis
    Sliding --> Redis

    MW --> View

    View --> Client
```

# Running the Project

## Clone the repository

```bash
git clone <repository-url>
cd rate-limiter
```

## Create a virtual environment

```bash
python -m venv venv
```

## Activate the environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Start Redis

Using Docker

```bash
docker run -d --name redis-server -p 6379:6379 redis
```

## Apply migrations

```bash
python manage.py migrate
```

## Start the server

```bash
python manage.py runserver
```

---

# Test the API

```
GET /api/public_api/
```

Send multiple requests within the configured window.

Once the limit is exceeded, the API returns:

```
HTTP 429 Too Many Requests
```

Example response:

```json
{
    "error": "Rate limit exceeded. Please try again later."
}
```

---

# Design Decisions

* **Middleware** keeps rate limiting separate from business logic.
* **Factory Pattern** allows switching algorithms without changing middleware.
* **Redis** provides fast in-memory operations and automatic expiration.
* **Custom Exceptions** keep the service layer clean and focused.
* **Configuration through settings.py** makes limits and algorithms easy to change.

---

# Future Improvements

* Token Bucket algorithm
* Leaky Bucket algorithm
* Endpoint-specific rate limits
* User-based rate limiting
* Rate limit response headers (`Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`)
* Automated unit and integration tests
* Monitoring and logging

---

# Learning Outcomes

This project helped me understand:

* Django Middleware
* Redis data structures
* Redis Sorted Sets
* Factory Pattern
* Exception-driven design
* Rate limiting algorithms
* Designing modular backend services
