---
name: python-standards
description: Python coding standards, conventions, and best practices. Use when writing, reviewing, or testing Python code.
---

# Python Coding Standards

## New Project Preferences

When starting new Python projects, prefer:

- **uv** for package/environment management (fast, modern alternative to pip/venv)
- **FastAPI** for web APIs
- **Pydantic** for data validation and serialization

## Style Guide

Follow PEP 8 with these project-specific additions:

### Formatting
- Line length: 88 characters (Black default)
- Use Black for formatting, isort for imports
- Use double quotes for strings (Black default)

### Naming Conventions
```python
# Modules and packages: lowercase_with_underscores
user_service.py

# Classes: PascalCase
class UserService:
    pass

# Functions and variables: snake_case
def get_user_by_id(user_id: int) -> User:
    active_users = []

# Constants: SCREAMING_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT_SECONDS = 30

# Private: single leading underscore
def _internal_helper():
    pass

# "Private" (name mangling): double leading underscore (rare)
class Base:
    def __private_method(self):
        pass
```

### Imports
```python
# Order: stdlib, third-party, local (isort handles this)
import os
import sys
from pathlib import Path

import requests
from pydantic import BaseModel

from app.models import User
from app.services import UserService
```

## Type Hints

Always use type hints for function signatures:

```python
from typing import Optional, List, Dict, Any, Union
from collections.abc import Sequence, Mapping

def process_users(
    users: List[User],
    filter_active: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> List[ProcessedUser]:
    """Process a list of users with optional filtering."""
    ...

# Use | for unions (Python 3.10+)
def get_value(key: str) -> str | None:
    ...
```

## Docstrings

Use Google-style docstrings:

```python
def fetch_user(user_id: int, include_deleted: bool = False) -> User:
    """Fetch a user by their ID.

    Args:
        user_id: The unique identifier of the user.
        include_deleted: Whether to include soft-deleted users.

    Returns:
        The User object if found.

    Raises:
        UserNotFoundError: If no user exists with the given ID.
        DatabaseConnectionError: If the database is unavailable.
    """
    ...
```

## Error Handling

```python
# Be specific with exceptions
try:
    user = await fetch_user(user_id)
except UserNotFoundError:
    logger.warning(f"User {user_id} not found")
    raise HTTPException(status_code=404, detail="User not found")
except DatabaseConnectionError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=503, detail="Service unavailable")

# Create custom exceptions for domain errors
class UserNotFoundError(Exception):
    """Raised when a user cannot be found."""
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} not found")
```

## Classes and Data

```python
# Prefer dataclasses for simple data containers
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    id: int
    email: str
    name: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

# Use Pydantic for validation and serialization
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    email: EmailStr
    name: str

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
```

## Async Code

```python
# Use async/await consistently
async def get_user_with_posts(user_id: int) -> UserWithPosts:
    async with get_db_session() as session:
        user = await session.get(User, user_id)
        posts = await session.execute(
            select(Post).where(Post.user_id == user_id)
        )
        return UserWithPosts(user=user, posts=posts.scalars().all())

# Use asyncio.gather for concurrent operations
async def fetch_all_data(user_id: int) -> tuple[User, list[Post], Settings]:
    user, posts, settings = await asyncio.gather(
        fetch_user(user_id),
        fetch_posts(user_id),
        fetch_settings(user_id),
    )
    return user, posts, settings
```

## Testing

```python
# Use pytest with fixtures
import pytest
from unittest.mock import Mock, patch, AsyncMock

@pytest.fixture
def mock_user():
    return User(id=1, email="test@example.com", name="Test User")

@pytest.fixture
def mock_db_session():
    with patch('app.database.get_session') as mock:
        yield mock

# Async tests
@pytest.mark.asyncio
async def test_fetch_user(mock_db_session, mock_user):
    mock_db_session.return_value.get = AsyncMock(return_value=mock_user)

    result = await fetch_user(1)

    assert result.id == 1
    assert result.email == "test@example.com"

# Parameterized tests
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("World", "WORLD"),
    ("", ""),
])
def test_uppercase(input, expected):
    assert uppercase(input) == expected
```

## Project Commands

Check `.claude/commands.md` for project-specific commands. Common Python commands:

```bash
# Virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Formatting
black .
isort .

# Linting
ruff check .
mypy .

# Testing
pytest
pytest --cov=app --cov-report=html
pytest -x -v  # stop on first failure, verbose
```

## Common Patterns

### Context Managers
```python
from contextlib import contextmanager, asynccontextmanager

@contextmanager
def temporary_file(suffix: str = ".tmp"):
    path = Path(tempfile.mktemp(suffix=suffix))
    try:
        yield path
    finally:
        path.unlink(missing_ok=True)

@asynccontextmanager
async def get_db_connection():
    conn = await create_connection()
    try:
        yield conn
    finally:
        await conn.close()
```

### Logging
```python
import logging

logger = logging.getLogger(__name__)

def process_order(order_id: int) -> None:
    logger.info(f"Processing order {order_id}")
    try:
        # ... processing
        logger.debug(f"Order {order_id} validated")
    except ValidationError as e:
        logger.warning(f"Order {order_id} validation failed: {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error processing order {order_id}")
        raise
```
