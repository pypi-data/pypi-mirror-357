"""
Интеграционные тесты с реальным API.

Эти тесты используют реальные креденшлы из .env файла.
Если креденшлы недоступны, тесты будут пропущены.
"""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from evolution_langchain import EvolutionInference

# Проверка доступности LangChain
try:
    import langchain  # noqa: F401

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


# Загрузка переменных окружения из .env файла
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def get_test_credentials():
    """Получение креденшлов для тестирования."""
    return {
        "model": os.getenv("EVOLUTION_MODEL"),
        "key_id": os.getenv("EVOLUTION_KEY_ID"),
        "secret": os.getenv("EVOLUTION_SECRET"),
        "base_url": os.getenv("EVOLUTION_BASE_URL"),
        "auth_url": os.getenv("EVOLUTION_TOKEN_URL"),
    }


def has_valid_credentials():
    """Проверка наличия всех необходимых креденшлов."""
    creds = get_test_credentials()
    required_fields = ["model", "key_id", "secret", "base_url"]

    return all(creds.get(field) for field in required_fields)


# Условие для пропуска тестов
skip_if_no_credentials = pytest.mark.skipif(
    not has_valid_credentials(),
    reason=(
        "Реальные креденшлы недоступны. Создайте .env файл с креденшлами "
        "или установите переменные окружения."
    ),
)

# Условие для пропуска тестов LangChain
skip_if_no_langchain = pytest.mark.skipif(
    not LANGCHAIN_AVAILABLE,
    reason="LangChain не установлен. Установите: poetry install --with dev",
)


@skip_if_no_credentials
class TestRealAPIIntegration:
    """Тесты с реальным API."""

    @pytest.fixture
    def llm(self):
        """Фикстура для создания LLM с реальными креденшлами."""
        creds = get_test_credentials()

        llm_kwargs = {
            "model": creds["model"],
            "key_id": creds["key_id"],
            "secret": creds["secret"],
            "base_url": creds["base_url"],
        }

        # Добавляем auth_url если он указан
        if creds["auth_url"]:
            llm_kwargs["auth_url"] = creds["auth_url"]

        # Добавляем дополнительные параметры если они указаны
        if temperature := os.getenv("EVOLUTION_TEMPERATURE"):
            llm_kwargs["temperature"] = float(temperature)

        if max_tokens := os.getenv("EVOLUTION_MAX_TOKENS"):
            llm_kwargs["max_tokens"] = int(max_tokens)

        if timeout := os.getenv("EVOLUTION_REQUEST_TIMEOUT"):
            llm_kwargs["request_timeout"] = int(timeout)

        return EvolutionInference(**llm_kwargs)

    def test_simple_invoke(self, llm):
        """Тест простого вызова с реальным API."""
        prompt = "Привет! Ответь одним словом: работаешь?"

        response = llm.invoke(prompt)

        assert isinstance(response, str)
        assert len(response) > 0
        print(f"✅ Ответ получен: {response}")

    def test_multiple_invokes(self, llm):
        """Тест нескольких последовательных вызовов."""
        prompts = ["Скажи 'один'", "Скажи 'два'", "Скажи 'три'"]

        responses = []
        for prompt in prompts:
            response = llm.invoke(prompt)
            responses.append(response)
            assert isinstance(response, str)
            assert len(response) > 0

        print(f"✅ Получено {len(responses)} ответов")
        for i, response in enumerate(responses, 1):
            print(f"  {i}. {response}")

    def test_token_refresh(self, llm):
        """Тест работы токенов (получение и потенциальное обновление)."""
        # Проверяем, что токен-менеджер создан
        assert hasattr(llm, "_token_manager")
        assert llm._token_manager is not None

        # Первый запрос - получение токена
        response1 = llm.invoke("Тест токена 1")
        assert isinstance(response1, str)
        assert len(response1) > 0

        # Проверяем, что токен получен
        assert llm._token_manager._token is not None
        assert llm._token_manager._token_expires_at > 0

        # Второй запрос - использование существующего токена
        response2 = llm.invoke("Тест токена 2")
        assert isinstance(response2, str)
        assert len(response2) > 0

        print("✅ Токен успешно получен и используется")

    def test_error_handling(self, llm):
        """Тест обработки ошибок с реальным API."""
        # Тест с очень длинным промптом (если есть ограничения)
        very_long_prompt = "Повтори это: " + "А" * 10000

        try:
            response = llm.invoke(very_long_prompt)
            # Если запрос прошел успешно
            assert isinstance(response, str)
            print("✅ Длинный промпт обработан успешно")
        except Exception as e:
            # Если возникла ошибка, проверяем что это осмысленная ошибка
            assert isinstance(e, (ValueError, RuntimeError))
            print(f"✅ Ошибка корректно обработана: {e}")

    def test_different_temperatures(self, llm):
        """Тест с разными параметрами temperature."""
        prompt = "Придумай одно слово"

        # Тест с низкой температурой (более детерминированный)
        llm.temperature = 0.1
        response_low = llm.invoke(prompt)

        # Тест с высокой температурой (более креативный)
        llm.temperature = 1.0
        response_high = llm.invoke(prompt)

        assert isinstance(response_low, str)
        assert isinstance(response_high, str)
        assert len(response_low) > 0
        assert len(response_high) > 0

        print(f"✅ Низкая temperature (0.1): {response_low}")
        print(f"✅ Высокая temperature (1.0): {response_high}")


@skip_if_no_credentials
@skip_if_no_langchain
class TestLangChainIntegration:
    """Тесты интеграции с LangChain."""

    @pytest.fixture
    def llm(self):
        """Фикстура для LLM."""
        creds = get_test_credentials()

        llm_kwargs = {
            "model": creds["model"],
            "key_id": creds["key_id"],
            "secret": creds["secret"],
            "base_url": creds["base_url"],
            "temperature": 0.7,
            "max_tokens": 200,
        }

        # Добавляем auth_url только если он не None
        if creds.get("auth_url"):
            llm_kwargs["auth_url"] = creds["auth_url"]

        return EvolutionInference(**llm_kwargs)

    def test_llm_chain(self, llm):
        """Тест LLMChain с реальным API."""
        from langchain.prompts import PromptTemplate

        template = "Ответь кратко на вопрос: {question}"
        prompt = PromptTemplate(
            template=template, input_variables=["question"]
        )
        chain = prompt | llm

        result = chain.invoke("Что такое Python?")

        assert isinstance(result, str)
        assert len(result) > 0
        assert "python" in result.lower()

        print(f"✅ LLMChain работает: {result}")

    def test_generate_method(self, llm):
        """Тест метода generate с множественными промптами."""
        prompts = ["Скажи 'А'", "Скажи 'Б'", "Скажи 'В'"]

        result = llm.generate(prompts)

        assert len(result.generations) == len(prompts)

        for i, generation in enumerate(result.generations):
            assert len(generation) > 0
            response = generation[0].text
            assert isinstance(response, str)
            assert len(response) > 0
            print(f"✅ Генерация {i + 1}: {response}")


# Дополнительная информация для отладки
def test_print_environment_info():
    """Информационный тест для отображения статуса окружения."""
    env_file_exists = (Path(__file__).parent.parent / ".env").exists()
    creds = get_test_credentials()

    print("\n" + "=" * 50)
    print("ИНФОРМАЦИЯ ОБ ОКРУЖЕНИИ")
    print("=" * 50)
    print(f"📁 .env файл существует: {env_file_exists}")
    print(f"🔑 EVOLUTION_MODEL: {'✓' if creds['model'] else '✗'}")
    print(f"🔑 EVOLUTION_KEY_ID: {'✓' if creds['key_id'] else '✗'}")
    print(f"🔑 EVOLUTION_SECRET: {'✓' if creds['secret'] else '✗'}")
    print(f"🔑 EVOLUTION_BASE_URL: {'✓' if creds['base_url'] else '✗'}")
    auth_status = "✓" if creds["auth_url"] else "✗ (опционально)"
    print(f"🔑 EVOLUTION_TOKEN_URL: {auth_status}")
    print(f"📦 LangChain доступен: {'✓' if LANGCHAIN_AVAILABLE else '✗'}")
    print(f"🧪 Тесты будут выполнены: {has_valid_credentials()}")
    langchain_tests_available = has_valid_credentials() and LANGCHAIN_AVAILABLE
    print(f"🧪 LangChain тесты: {langchain_tests_available}")

    if not has_valid_credentials():
        print("\n💡 Чтобы запустить интеграционные тесты:")
        print("   1. Скопируйте env.example в .env")
        print("   2. Заполните .env своими креденшлами")
        print("   3. Или установите переменные окружения")

    if not LANGCHAIN_AVAILABLE:
        print("\n💡 Чтобы запустить LangChain тесты:")
        print("   1. Установите dev зависимости: poetry install --with dev")
        print("   2. Или: pip install langchain")

    print("=" * 50 + "\n")
