#!/usr/bin/env python3
"""
Примеры использования стриминга в EvolutionInference LLM
"""

import os
import time

from evolution_langchain import EvolutionInference


def demo_streaming_basic():
    """Демонстрация базового стриминга"""
    print("🌊 Демонстрация стриминга")
    print("=" * 50)

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
        print("⚠️ Переменные окружения не настроены")
        print("💡 Пример будет показан в демонстрационном режиме")
        print()

    # Создание LLM с включенным стримингом
    llm = EvolutionInference(
        model="your-model-name",
        key_id=os.getenv("EVOLUTION_KEY_ID", "your-key-id"),
        secret=os.getenv("EVOLUTION_SECRET", "your-secret"),
        base_url=os.getenv(
            "EVOLUTION_BASE_URL", "https://your-api-endpoint.com/v1"
        ),
        max_tokens=500,
        temperature=0.7,
        stream=True,  # Включаем стриминг
    )

    print("✅ LLM с стримингом инициализирован")
    print(f"📝 Модель: {llm.model}")
    print(f"🌊 Стриминг: {llm.stream}")
    print()

    # Пример стриминга
    prompt = (
        "Расскажи историю о маленьком роботе, который мечтал стать художником"
    )
    print(f"💬 Запрос: {prompt}")
    print("🌊 Ответ (стриминг):")

    if has_credentials:
        try:
            # Выполняем стриминг
            response = llm.invoke(prompt)
            print("\n✅ Стриминг завершен")
            print(f"📝 Полный ответ: {response}")
        except Exception as e:
            print(f"❌ Ошибка при стриминге: {e}")
            print("💡 Проверьте правильность учетных данных и доступность API")
    else:
        print("⚠️ Стриминг не выполнен (демо-режим)")
        print("💡 Для реального стриминга настройте переменные окружения")
        print("🌊 Демо-ответ: Привет! Я маленький робот...")
        time.sleep(0.5)
        print("🌊 Демо-ответ: ...который мечтал стать художником...")
        time.sleep(0.5)
        print("🌊 Демо-ответ: ...и однажды он нашел кисть...")
        time.sleep(0.5)
        print("🌊 Демо-ответ: ...и начал рисовать прекрасные картины!")


def demo_streaming_with_callbacks():
    """Демонстрация стриминга с кастомными колбэками"""
    print("\n🔄 Стриминг с кастомными колбэками")
    print("=" * 50)

    print("💡 В реальном использовании можно добавить:")
    print("   - Прогресс-бар")
    print("   - Сохранение в файл")
    print("   - Отправка в чат")
    print("   - Логирование")
    print("   - Аналитика")

    print("\n🔧 Пример кастомного колбэка:")
    print("""
class StreamingCallback:
    def on_llm_start(self, serialized, prompts, **kwargs):
        print("🚀 Начало генерации...")
    def on_llm_new_token(self, token, **kwargs):
        print(token, end="", flush=True)
    def on_llm_end(self, response, **kwargs):
        print("\\n✅ Генерация завершена")
    """)


def demo_streaming_configuration():
    """Демонстрация конфигурации стриминга"""
    print("\n⚙️ Конфигурация стриминга")
    print("=" * 50)

    print("🔧 Доступные параметры:")
    print("   stream=True/False - включить/выключить стриминг")
    print("   max_tokens - максимальное количество токенов")
    print("   temperature - креативность ответов")
    print("   top_p - разнообразие ответов")
    print("   frequency_penalty - штраф за повторения")
    print("   presence_penalty - штраф за присутствие слов")

    print("\n💡 Рекомендации:")
    print("   - Используйте стриминг для длинных ответов")
    print("   - Настройте max_tokens для контроля длины")
    print("   - Добавьте обработку ошибок")
    print("   - Используйте колбэки для кастомизации")


def main():
    """Главная функция"""
    print("🚀 Evolution LangChain - Примеры стриминга")
    print("=" * 60)

    demo_streaming_basic()
    demo_streaming_with_callbacks()
    demo_streaming_configuration()

    print("\n🎉 Демонстрация стриминга завершена!")
    print("📚 См. документацию для подробной информации")


if __name__ == "__main__":
    main()
