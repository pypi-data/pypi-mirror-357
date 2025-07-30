"""
Pytest configuration and fixtures for evolution-langchain tests
"""

from __future__ import annotations

import os
import logging
from typing import TYPE_CHECKING, Dict, Iterator, AsyncIterator

import pytest
from dotenv import load_dotenv
from pytest_asyncio import is_async_test

from evolution_langchain import EvolutionInference

if TYPE_CHECKING:
    from _pytest.config import (
        Config,  # pyright: ignore[reportPrivateImportUsage]
    )

pytest.register_assert_rewrite("tests.utils")

logging.getLogger("evolution_langchain").setLevel(logging.DEBUG)

# Load .env file if it exists
load_dotenv()


# automatically add `pytest.mark.asyncio()` to all of our async tests
# so we don't have to add that boilerplate everywhere
def pytest_collection_modifyitems(items: list[pytest.Function]) -> None:
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)

    # Skip integration tests if not enabled
    if not os.getenv("ENABLE_INTEGRATION_TESTS", "false").lower() == "true":
        skip_integration = pytest.mark.skip(
            reason="Integration tests disabled. "
            "Set ENABLE_INTEGRATION_TESTS=true to enable."
        )
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)


def pytest_configure(config: Config) -> None:
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "slow: mark test as slow running")

    # Load environment variables from .env file if exists
    try:
        from dotenv import load_dotenv

        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"✅ Loaded .env file: {env_path}")
    except ImportError:
        # python-dotenv not installed - not critical for tests
        pass


@pytest.fixture(scope="session")
def test_credentials() -> Dict[str, str]:
    """Fixture providing test credentials from environment variables"""
    return {
        "key_id": os.getenv("EVOLUTION_KEY_ID", ""),
        "secret": os.getenv("EVOLUTION_SECRET", ""),
        "base_url": os.getenv("EVOLUTION_BASE_URL", ""),
        "auth_url": os.getenv(
            "EVOLUTION_AUTH_URL", "https://iam.api.cloud.ru/api/v1/auth/token"
        ),
        "model": os.getenv("EVOLUTION_MODEL", "evolution-1"),
    }


@pytest.fixture(scope="session")
def integration_enabled() -> bool:
    """Fixture checking if integration tests are enabled"""
    return os.getenv("ENABLE_INTEGRATION_TESTS", "false").lower() == "true"


@pytest.fixture
def mock_credentials() -> Dict[str, str]:
    """Fixture providing mock credentials for unit tests"""
    return {
        "key_id": "test_key_id",
        "secret": "test_secret",
        "base_url": "https://test.example.com/v1",
        "auth_url": "https://iam.api.cloud.ru/api/v1/auth/token",
        "model": "test-model",
    }


@pytest.fixture(scope="session")
def client(test_credentials: Dict[str, str]) -> Iterator[EvolutionInference]:
    """Session-scoped EvolutionInference client fixture with proper cleanup"""
    if not test_credentials["key_id"] or not test_credentials["secret"]:
        pytest.skip("Real credentials not provided for client fixture")

    try:
        client = EvolutionInference(
            key_id=test_credentials["key_id"],
            secret=test_credentials["secret"],
            base_url=test_credentials["base_url"],
            auth_url=test_credentials["auth_url"],
            model=test_credentials["model"],
            max_tokens=512,
            temperature=0.7,
            request_timeout=30,
        )
        yield client
    except Exception as e:
        pytest.skip(f"Failed to create EvolutionInference client: {e}")


@pytest.fixture(scope="session")
async def async_client(
    test_credentials: Dict[str, str],
) -> AsyncIterator[EvolutionInference]:
    """Session-scoped async EvolutionInference client fixture with proper cleanup"""
    if not test_credentials["key_id"] or not test_credentials["secret"]:
        pytest.skip("Real credentials not provided for async client fixture")

    try:
        client = EvolutionInference(
            key_id=test_credentials["key_id"],
            secret=test_credentials["secret"],
            base_url=test_credentials["base_url"],
            auth_url=test_credentials["auth_url"],
            model=test_credentials["model"],
            max_tokens=512,
            temperature=0.7,
            request_timeout=30,
        )
        yield client
    except Exception as e:
        pytest.skip(f"Failed to create async EvolutionInference client: {e}")


@pytest.fixture
def mock_evolution_client(
    mock_credentials: Dict[str, str],
) -> EvolutionInference:
    """Fixture providing a mock EvolutionInference client for unit tests"""
    return EvolutionInference(
        key_id=mock_credentials["key_id"],
        secret=mock_credentials["secret"],
        base_url=mock_credentials["base_url"],
        auth_url=mock_credentials["auth_url"],
        model=mock_credentials["model"],
        max_tokens=100,
        temperature=0.5,
    )
