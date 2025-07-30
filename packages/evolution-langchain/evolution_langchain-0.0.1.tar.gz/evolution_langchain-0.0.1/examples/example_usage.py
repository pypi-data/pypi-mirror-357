#!/usr/bin/env python3
"""
Пример использования EvolutionInference LLM
"""

import os

from evolution_langchain import EvolutionInference


def main():
    print("🚀 Пример использования EvolutionInference LLM")
    print("=" * 60)

    # Проверяем наличие переменных окружения
    has_credentials = all(
        [
            os.getenv("EVOLUTION_KEY_ID")
            and os.getenv("EVOLUTION_KEY_ID") != "your_key_id_here",
            os.getenv("EVOLUTION_SECRET")
            and os.getenv("EVOLUTION_SECRET") != "your_secret_here",
            os.getenv("EVOLUTION_BASE_URL")
            and os.getenv("EVOLUTION_BASE_URL")
            != "https://your-endpoint.cloud.ru/v1",
        ]
    )

    if not has_credentials:
        print("⚠️ Переменные окружения не настроены или содержат демо-значения")
        print("💡 Пример будет показан в демонстрационном режиме")
        print()

    # Инициализация модели с учетными данными
    llm = EvolutionInference(
        model="your-model-name",  # Укажите название модели
        key_id=os.getenv("EVOLUTION_KEY_ID", "your-key-id"),
        secret=os.getenv("EVOLUTION_SECRET", "your-secret"),
        base_url=os.getenv(
            "EVOLUTION_BASE_URL", "https://your-api-endpoint.com/v1"
        ),
        max_tokens=1000,
        temperature=0.7,
        top_p=0.9,
    )

    print("✅ LLM успешно инициализирован")
    print(f"📝 Модель: {llm.model}")
    print(f"🌐 Base URL: {llm.base_url}")
    print(f"🌡️ Температура: {llm.temperature}")
    print(f"🎯 Max tokens: {llm.max_tokens}")
    print()

    # Простой запрос
    print("💬 Пример простого запроса:")
    prompt = "Привет! Как дела?"
    print(f"Запрос: {prompt}")

    if has_credentials:
        try:
            response = llm.invoke(prompt)
            print("Ответ модели:", response)
        except Exception as e:
            print(f"❌ Ошибка при выполнении запроса: {e}")
            print("💡 Проверьте правильность учетных данных и доступность API")
    else:
        print("⚠️ Запрос не выполнен (демо-режим)")
        print("💡 Для реального запроса настройте переменные окружения")

    print()

    # Пакетный запрос
    print("📦 Пример пакетного запроса:")
    prompts = [
        "Что такое машинное обучение?",
        "Объясни принцип работы нейронных сетей",
        "Какие преимущества у Python для ML?",
    ]

    for i, prompt in enumerate(prompts, 1):
        print(f"{i}. {prompt}")

    if has_credentials:
        try:
            print("\nВыполнение пакетного запроса...")
            responses = llm.generate(prompts)
            for i, response in enumerate(responses.generations):
                print(f"Ответ на вопрос {i + 1}: {response[0].text}")
        except Exception as e:
            print(f"❌ Ошибка при выполнении пакетного запроса: {e}")
    else:
        print("\n⚠️ Пакетный запрос не выполнен (демо-режим)")
        print("💡 Для реального запроса настройте переменные окружения")

    print("\n🎉 Пример завершен!")
    print("📚 См. документацию для подробной информации")


if __name__ == "__main__":
    main()
