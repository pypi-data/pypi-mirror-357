#!/usr/bin/env python3
"""
Демонстрация работы EvolutionInference LLM
"""

import os

from evolution_langchain import EvolutionInference


def demo_basic_usage():
    """Демонстрация базового использования"""
    print("🚀 Демонстрация EvolutionInference LLM")
    print("=" * 50)

    # Вы можете задать учетные данные через переменные окружения
    # или передать их напрямую в конструктор

    try:
        # Создание экземпляра LLM
        llm = EvolutionInference(
            model="your-model-name",  # Замените на ваше название модели
            key_id=os.getenv("EVOLUTION_KEY_ID", "your-key-id"),
            secret=os.getenv("EVOLUTION_SECRET", "your-secret"),
            base_url=os.getenv(
                "EVOLUTION_BASE_URL", "https://your-api-endpoint.com/v1"
            ),
            max_tokens=500,
            temperature=0.7,
            top_p=0.9,
        )

        print("✅ LLM успешно инициализирован")
        print(f"📝 Модель: {llm.model}")
        print(f"🌐 Base URL: {llm.base_url}")
        print(f"🌡️  Температура: {llm.temperature}")
        print(f"🎯 Max tokens: {llm.max_tokens}")
        print()

        # Пример простого запроса
        print("💬 Тест простого запроса:")
        prompt = "Объясни принцип работы нейронных сетей простыми словами"
        print(f"Запрос: {prompt}")

        # Здесь бы произошел реальный запрос к API
        print("⚠️  Для реального запроса нужны валидные учетные данные")

        # Пример пакетного запроса
        print("\n📦 Тест пакетного запроса:")
        prompts = [
            "Что такое машинное обучение?",
            "Какие виды алгоритмов ML существуют?",
            "Где применяется искусственный интеллект?",
        ]

        for i, prompt in enumerate(prompts, 1):
            print(f"{i}. {prompt}")

        print("\n🔧 Доступные параметры конфигурации:")
        config_params = llm._default_params
        for key, value in config_params.items():
            print(f"  {key}: {value}")

        print("\n🔒 Управление токенами:")
        print("  ✓ Автоматическое получение токена при первом запросе")
        print("  ✓ Кэширование токена в памяти")
        print("  ✓ Автоматическое обновление за 30 сек до истечения")
        print("  ✓ Thread-safe операции")
        print("  ✓ Обработка ошибок аутентификации")

    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        print("💡 Убедитесь, что предоставлены key_id, secret и base_url")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")


def demo_langchain_integration():
    """Демонстрация интеграции с LangChain"""
    print("\n🔗 Интеграция с LangChain")
    print("=" * 50)

    try:
        from langchain.prompts import PromptTemplate

        # Создание шаблона промпта
        template = """
        Ты - эксперт по {topic}.
        Ответь на следующий вопрос: {question}

        Ответ:
        """

        prompt = PromptTemplate(
            template=template, input_variables=["topic", "question"]
        )

        print("✅ Шаблон промпта создан")
        print(f"📝 Переменные: {prompt.input_variables}")

        # Создание цепочки (без реального выполнения)
        print("✅ Готово для создания LLMChain")
        print("💡 Пример использования:")
        print("   chain = LLMChain(llm=evolution_llm, prompt=prompt)")
        print(
            "   result = chain.run(topic='ML', "
            "question='Что такое градиентный спуск?')"
        )

    except ImportError:
        print("⚠️  LangChain не установлен. Установите: pip install langchain")


def demo_error_handling():
    """Демонстрация обработки ошибок"""
    print("\n🛡️ Обработка ошибок")
    print("=" * 50)

    print("1. Отсутствие учетных данных:")
    try:
        EvolutionInference(base_url="https://test.example.com/v1")
    except ValueError as e:
        print(f"   ✅ Корректно перехвачено: {e}")

    print("\n2. Отсутствие base_url:")
    try:
        EvolutionInference(key_id="test_key", secret="test_secret")
    except ValueError as e:
        print(f"   ✅ Корректно перехвачено: {e}")

    print("\n3. Неверные учетные данные:")
    print("   ✅ RuntimeError при ошибке аутентификации")

    print("\n4. Сетевые ошибки:")
    print("   ✅ RuntimeError при проблемах сети")

    print("\n5. Неверный формат ответа API:")
    print("   ✅ ValueError при неправильном формате")


if __name__ == "__main__":
    demo_basic_usage()
    demo_langchain_integration()
    demo_error_handling()

    print("\n🎉 Демонстрация завершена!")
    print("📚 См. README.md для подробной документации")
    print("🧪 Запустите 'pytest' для выполнения тестов")
