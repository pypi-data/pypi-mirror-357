from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError

from evolution_langchain.evolution_inference import (
    TokenManager,
    EvolutionInference,
)


class TestTokenManager:
    """Тесты для класса TokenManager"""

    def test_init(self):
        """Тест инициализации TokenManager"""
        manager = TokenManager("test_key", "test_secret")
        assert manager.key_id == "test_key"
        assert manager.secret == "test_secret"
        assert manager._token is None
        assert manager._token_expires_at == 0

    @patch("requests.post")
    def test_refresh_token_success(self, mock_post):
        """Тест успешного обновления токена"""
        # Mock успешного ответа
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "test_token_123",
            "expires_in": 3600,
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        manager = TokenManager("test_key", "test_secret")
        token = manager._refresh_token()

        assert token == "test_token_123"
        assert manager._token == "test_token_123"
        assert manager._token_expires_at > 0

        # Проверяем правильность запроса
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "test_key" in call_args.kwargs["data"]
        assert "test_secret" in call_args.kwargs["data"]

    @patch("requests.post")
    def test_refresh_token_failure(self, mock_post):
        """Тест неудачного обновления токена"""
        import requests

        mock_post.side_effect = requests.RequestException("Network error")

        manager = TokenManager("test_key", "test_secret")

        with pytest.raises(
            RuntimeError, match=r"Failed to obtain access token"
        ):
            manager._refresh_token()

    @patch("time.time")
    @patch("requests.post")
    def test_get_token_cached(self, mock_post, mock_time):
        """Тест получения кэшированного токена"""
        # Настройка времени
        mock_time.return_value = 1000

        # Mock для первого запроса
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "cached_token",
            "expires_in": 3600,
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        manager = TokenManager("test_key", "test_secret")

        # Первый вызов - должен сделать запрос
        token1 = manager.get_token()
        assert token1 == "cached_token"
        assert mock_post.call_count == 1

        # Второй вызов - должен вернуть кэшированный токен
        token2 = manager.get_token()
        assert token2 == "cached_token"
        # Запрос не должен повториться
        assert mock_post.call_count == 1


class TestEvolutionInference:
    """Тесты для класса EvolutionInference"""

    def test_init_missing_credentials(self):
        """Тест инициализации без учетных данных"""
        with pytest.raises(
            ValueError, match=r"key_id and secret must be provided"
        ):
            EvolutionInference(base_url="https://test.example.com/v1")

    def test_init_missing_base_url(self):
        """Тест инициализации без base_url"""
        with pytest.raises(ValidationError):
            EvolutionInference(key_id="test_key", secret="test_secret")

    @patch.object(TokenManager, "__init__", return_value=None)
    def test_init_success(self, mock_token_manager):
        """Тест успешной инициализации"""
        llm = EvolutionInference(
            model="test-model",
            key_id="test_key",
            secret="test_secret",
            base_url="https://test.example.com/v1",
        )

        assert llm.model == "test-model"
        assert llm.base_url == "https://test.example.com/v1"
        assert hasattr(llm, "_token_manager")
        mock_token_manager.assert_called_once()

    @patch("requests.post")
    @patch.object(TokenManager, "get_token", return_value="test_token")
    def test_generate_success(self, mock_get_token, mock_post):
        """Тест успешной генерации"""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Тестовый ответ"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        llm = EvolutionInference(
            model="test-model",
            key_id="test_key",
            secret="test_secret",
            base_url="https://test.example.com/v1",
        )

        result = llm._generate(["Тестовый промпт"])

        assert len(result.generations) == 1
        assert len(result.generations[0]) == 1
        assert result.generations[0][0].text == "Тестовый ответ"

        # Проверяем правильность запроса
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        auth_header = call_args.kwargs["headers"]["Authorization"]
        assert "Bearer test_token" in auth_header
        # Проверяем что используется правильный URL
        expected_url = "https://test.example.com/v1/chat/completions"
        assert call_args[0][0] == expected_url

    @patch("requests.post")
    @patch.object(TokenManager, "get_token", return_value="test_token")
    def test_generate_api_error(self, mock_get_token, mock_post):
        """Тест обработки ошибки API"""
        import requests

        # Mock API error
        mock_post.side_effect = requests.RequestException("API Error")

        llm = EvolutionInference(
            model="test-model",
            key_id="test_key",
            secret="test_secret",
            base_url="https://test.example.com/v1",
        )

        with pytest.raises(RuntimeError, match=r"API request failed"):
            llm._generate(["Тестовый промпт"])

    @patch.object(TokenManager, "__init__", return_value=None)
    def test_default_params(self, mock_token_manager):
        """Тест параметров по умолчанию"""
        llm = EvolutionInference(
            model="test-model",
            key_id="test_key",
            secret="test_secret",
            base_url="https://test.example.com/v1",
            max_tokens=1000,
            temperature=0.8,
        )

        params = llm._default_params
        assert params["model"] == "test-model"
        assert params["max_tokens"] == 1000
        assert params["temperature"] == 0.8

    @patch.object(TokenManager, "__init__", return_value=None)
    def test_llm_type(self, mock_token_manager):
        """Тест типа LLM"""
        llm = EvolutionInference(
            model="test-model",
            key_id="test_key",
            secret="test_secret",
            base_url="https://test.example.com/v1",
        )

        assert llm._llm_type == "cloud-ru-tech"
