# Evolution LangChain
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/evolution-langchain.svg)](https://badge.fury.io/py/evolution-langchain)
[![Coverage](https://cloud-ru-tech.github.io/evolution-langchain/badges/coverage.svg)](https://github.com/cloud-ru-tech/evolution-langchain/actions)

**Полностью совместимая** интеграция Evolution Inference API с LangChain, включающая автоматическое управление токенами доступа. Просто замените стандартные LLM на `EvolutionInference` и все будет работать!

## 🎯 Особенности

- ✅ **100% совместимость** с LangChain LLM интерфейсом
- ✅ **Автоматическое управление токенами** Cloud.ru
- ✅ **Drop-in replacement** - минимальные изменения в коде
- ✅ **Async/await поддержка** с асинхронными методами
- ✅ **Streaming responses** поддержка
- ✅ **Thread-safe** token management
- ✅ **Автоматическое обновление** токенов за 30 секунд до истечения
- ✅ **Retry логика** при ошибках авторизации
- ✅ **Поддержка .env файлов** для управления конфигурацией
- ✅ **Интеграционные тесты** с реальным API

## 📦 Установка

### Требования

- Python 3.9+
- Pydantic 2.7.4+ (автоматически устанавливается)
- LangChain 0.3.25+ (автоматически устанавливается)
- [Poetry](https://python-poetry.org/docs/#installation) (рекомендуется)

### Установка через pip

```bash
pip install evolution-langchain
```

### Установка через Poetry (рекомендуется)

```bash
# Клонируйте репозиторий
git clone https://github.com/cloud-ru-tech/evolution-langchain.git
cd evolution-langchain

# Установите зависимости
poetry install

# Активируйте виртуальное окружение
poetry shell
```

### Установка из исходного кода

```bash
# Клонируйте репозиторий
git clone https://github.com/cloud-ru-tech/evolution-langchain.git
cd evolution-langchain

# Установите в режиме разработки
pip install -e .

# Или установите обычным способом
pip install .
```

## ⚡ Быстрый старт

### Миграция с стандартных LLM

```python
# ❌ БЫЛО (стандартный LangChain LLM)
from langchain.llms import OpenAI

llm = OpenAI(api_key="sk-...")

# ✅ СТАЛО (Evolution LangChain)
from evolution_langchain import EvolutionInference

llm = EvolutionInference(
    model="your-model-name",
    key_id="your_key_id", 
    secret="your_secret", 
    base_url="https://your-model-endpoint.cloud.ru/v1"
)

# Все остальное работает ТОЧНО ТАК ЖЕ!
response = llm.invoke("Hello!")
```

### Основное использование

```python
from evolution_langchain import EvolutionInference

# Инициализация модели
llm = EvolutionInference(
    model="your-model-name",
    key_id="your-key-id",
    secret="your-secret",
    base_url="https://your-api-endpoint.com/v1",  # Обязательный параметр
    max_tokens=1000,
    temperature=0.7,
)

# Простой запрос
response = llm.invoke("Привет! Расскажи о себе.")
print(response)

# Пакетная обработка
prompts = [
    "Что такое машинное обучение?",
    "Объясни принцип работы нейронных сетей"
]
responses = llm.generate(prompts)
```

### Интеграция с LangChain

```python
from evolution_langchain import EvolutionInference
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Создание шаблона промпта
template = "Ответь на вопрос: {question}"
prompt = PromptTemplate(template=template, input_variables=["question"])

# Создание цепочки с Evolution Inference
llm = EvolutionInference(
    model="your-model", 
    key_id="your-key-id", 
    secret="your-secret",
    base_url="https://your-api-endpoint.com/v1"
)
chain = LLMChain(llm=llm, prompt=prompt)

# Выполнение
result = chain.run("Что такое квантовые компьютеры?")
print(result)
```

## 🔧 Конфигурация

### Переменные окружения

Создайте файл `.env` в корне вашего проекта:

```bash
# Скопируйте из env.example и заполните
cp env.example .env
```

```bash
# .env файл
EVOLUTION_KEY_ID=your_key_id_here
EVOLUTION_SECRET=your_secret_here
EVOLUTION_BASE_URL=https://your-model-endpoint.cloud.ru/v1
EVOLUTION_MODEL=your-model-name
ENABLE_INTEGRATION_TESTS=false
LOG_LEVEL=INFO
```

```python
import os
from evolution_langchain import EvolutionInference
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

llm = EvolutionInference(
    model=os.getenv("EVOLUTION_MODEL"),
    key_id=os.getenv("EVOLUTION_KEY_ID"),
    secret=os.getenv("EVOLUTION_SECRET"),
    base_url=os.getenv("EVOLUTION_BASE_URL")
)
```

### Параметры конфигурации

| Параметр | Тип | Описание | По умолчанию |
|----------|-----|----------|-------------|
| `model` | str | Название модели | "" |
| `key_id` | str | ID ключа для аутентификации | **обязательный** |
| `secret` | str | Секрет для аутентификации | **обязательный** |
| `base_url` | str | URL API Evolution Inference | **обязательный** |
| `auth_url` | str | URL сервера аутентификации | предустановлен |
| `max_tokens` | int | Максимальное количество токенов | 512 |
| `temperature` | float | Контроль случайности (0.0-2.0) | 1.0 |
| `top_p` | float | Nucleus sampling (0.0-1.0) | 1.0 |
| `frequency_penalty` | float | Штраф за частоту (-2.0-2.0) | 0.0 |
| `presence_penalty` | float | Штраф за присутствие (-2.0-2.0) | 0.0 |
| `stop` | List[str] | Стоп-последовательности | None |
| `request_timeout` | int | Таймаут запроса в секундах | 60 |

## 🔍 Управление токенами

Класс автоматически управляет жизненным циклом токенов:

- ✅ Автоматическое получение токена при первом запросе
- ✅ Кэширование токена в памяти
- ✅ Автоматическое обновление за 30 секунд до истечения
- ✅ Thread-safe операции с токенами
- ✅ Обработка ошибок аутентификации

## 📋 Полная совместимость

Поддерживаются ВСЕ методы LangChain LLM интерфейса:

```python
# Основные методы
llm.invoke("Hello world")
llm.generate(["prompt1", "prompt2"])

# Асинхронные методы
await llm.ainvoke("Hello world")
await llm.agenerate(["prompt1", "prompt2"])

# Стриминг
for chunk in llm.stream("Tell me a story"):
    print(chunk, end="")

# Интеграция с цепочками
from langchain.chains import LLMChain
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run("Your question here")
```

## 🧪 Примеры

### Запуск всех примеров

```bash
# Запуск всех примеров с детальной отчетностью
make run-all-examples
```

### Запуск отдельных примеров

```bash
# Базовые примеры использования
make run-examples

# Демонстрация возможностей
make run-demo

# Примеры стриминга
make run-streaming
```

### Доступные примеры

- **`demo.py`** - Демонстрация основных возможностей и интеграции с LangChain
- **`example_usage.py`** - Базовое использование API с простыми и пакетными запросами
- **`streaming_examples.py`** - Примеры использования стриминга для длинных ответов

### Настройка окружения для примеров

1. Создайте файл `.env`:
```bash
cp env.example .env
```

2. Заполните переменные окружения:
```bash
EVOLUTION_KEY_ID=your_key_id_here
EVOLUTION_SECRET=your_secret_here
EVOLUTION_BASE_URL=https://your-endpoint.cloud.ru/v1
```

3. Запустите примеры:
```bash
make run-all-examples
```

## Обработка ошибок

```python
from evolution_langchain import EvolutionInference

try:
    llm = EvolutionInference(
        model="your-model",
        key_id="invalid-key",
        secret="invalid-secret",
        base_url="https://your-api-endpoint.com/v1"
    )
    response = llm.invoke("Test")
except ValueError as e:
    print(f"Ошибка конфигурации: {e}")
except RuntimeError as e:
    print(f"Ошибка API: {e}")
```

## 🆘 Support

- [GitHub Issues](https://github.com/cloud-ru-tech/evolution-langchain/issues)
- [Documentation](https://cloud-ru-tech.github.io/evolution-langchain)
- Email: support@cloud.ru

## 🔗 Links

- [PyPI Package](https://pypi.org/project/evolution-langchain/)
- [GitHub Repository](https://github.com/cloud-ru-tech/evolution-langchain)
- [Cloud.ru Platform](https://cloud.ru/)
- [LangChain Documentation](https://python.langchain.com/)