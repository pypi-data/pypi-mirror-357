#!/usr/bin/env python3
"""
Evolution LangChain - Запуск всех примеров
"""

import os
import sys
import time
import subprocess
from enum import Enum
from typing import Dict, List, Tuple
from pathlib import Path
from dataclasses import dataclass

# Загружаем переменные окружения из файла .env если он существует
try:
    from dotenv import load_dotenv  # type: ignore

    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Переменные окружения загружены из {env_file}")
    else:
        print(
            "ℹ️ Файл .env не найден, используются системные переменные окружения"
        )
except ImportError:
    print(
        "⚠️ python-dotenv недоступен, используются только системные переменные окружения"
    )

# Добавляем путь к родительской директории для импорта
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))


class ExampleStatus(Enum):
    """Статусы выполнения примеров"""

    SUCCESS = "✅"
    FAILED = "❌"
    SKIPPED = "⏭️"
    TIMEOUT = "⏱️"
    ERROR = "💥"


@dataclass
class ExampleResult:
    """Результат выполнения примера"""

    name: str
    description: str
    status: ExampleStatus
    duration: float
    output: str
    error: str = ""
    return_code: int = 0


class ExampleRunner:
    """Класс для запуска и управления примерами"""

    def __init__(self):
        self.examples_dir = Path(__file__).parent
        self.results: List[ExampleResult] = []
        self.start_time = time.time()

    def check_environment(self) -> Dict[str, bool]:
        """Проверяет наличие переменных окружения"""
        required_vars = [
            "EVOLUTION_KEY_ID",
            "EVOLUTION_SECRET",
            "EVOLUTION_BASE_URL",
        ]

        env_status: Dict[str, bool] = {}
        for var in required_vars:
            env_status[var] = bool(os.getenv(var))

        return env_status

    def print_header(self):
        """Выводит заголовок"""
        print("🚀 Evolution LangChain - Запуск всех примеров")
        print("=" * 80)
        print(f"📅 Время запуска: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Директория примеров: {self.examples_dir}")
        print()

    def print_environment_info(self):
        """Выводит информацию о переменных окружения"""
        env_status = self.check_environment()
        missing_vars = [
            var for var, present in env_status.items() if not present
        ]

        print("🔧 Проверка переменных окружения:")
        for var, present in env_status.items():
            status = "✅" if present else "❌"
            print(f"   {status} {var}")

        if missing_vars:
            print(
                f"\n⚠️ Отсутствуют переменные окружения: {', '.join(missing_vars)}"
            )
            print("💡 Примеры будут запущены в демонстрационном режиме")
            print("Для полного тестирования установите:")
            print("   export EVOLUTION_KEY_ID='your_key_id'")
            print("   export EVOLUTION_SECRET='your_secret'")
            print(
                "   export EVOLUTION_BASE_URL='https://your-endpoint.cloud.ru/v1'"
            )
        else:
            print("\n✅ Все необходимые переменные окружения установлены")
            print("Примеры будут работать с реальным API")

        print()

    def get_examples(self) -> List[Tuple[str, str]]:
        """Возвращает список примеров для запуска"""
        return [
            ("demo.py", "Демонстрация основных возможностей"),
            ("example_usage.py", "Базовое использование API"),
            ("streaming_examples.py", "Примеры стриминга"),
        ]

    def run_example(self, script_name: str, description: str) -> ExampleResult:
        """Запускает отдельный пример"""
        print(f"\n{'=' * 80}")
        print(f"🔧 {description}")
        print(f"📄 Файл: {script_name}")
        print("=" * 80)

        script_path = self.examples_dir / script_name
        if not script_path.exists():
            return ExampleResult(
                name=script_name,
                description=description,
                status=ExampleStatus.ERROR,
                duration=0.0,
                output="",
                error=f"Файл {script_name} не найден",
                return_code=1,
            )

        start_time = time.time()
        output = ""
        error_output = ""
        return_code = 0

        try:
            # Запуск примера
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=60,  # Увеличиваем таймаут до 60 секунд
                env=os.environ.copy(),
            )

            output = result.stdout
            error_output = result.stderr
            return_code = result.returncode

            if output:
                print(output)

            if error_output:
                print(f"⚠️ Предупреждения/ошибки:\n{error_output}")

            # Анализ результата
            duration = time.time() - start_time

            # Проверяем на реальные API ошибки
            has_api_errors = any(
                error_pattern in output
                for error_pattern in [
                    "Error code: 404",
                    "Error code: 401",
                    "Error code: 403",
                    "Error code: 500",
                    "ConnectionError",
                    "TimeoutError",
                ]
            )

            # Проверяем на отсутствие переменных окружения (это ожидаемо)
            has_env_issues = any(
                env_pattern in output
                for env_pattern in [
                    "Установите переменные окружения",
                    "your_key_id",
                    "your_secret",
                    "key_id и secret обязательны",
                ]
            )

            if return_code == 0:
                if has_api_errors and not has_env_issues:
                    status = ExampleStatus.FAILED
                    error_msg = "API ошибки при выполнении"
                else:
                    status = ExampleStatus.SUCCESS
                    error_msg = ""
            else:
                status = ExampleStatus.FAILED
                error_msg = f"Код возврата: {return_code}"

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            status = ExampleStatus.TIMEOUT
            error_msg = "Прервано по таймауту"
            print(f"⏱️ {script_name} прерван по таймауту")

        except Exception as e:
            duration = time.time() - start_time
            status = ExampleStatus.ERROR
            error_msg = str(e)
            print(f"💥 Ошибка при запуске {script_name}: {e}")

        # Выводим статус
        status_emoji = status.value
        print(f"\n{status_emoji} {script_name} - {status.name}")
        print(f"⏱️ Время выполнения: {duration:.2f} сек")

        return ExampleResult(
            name=script_name,
            description=description,
            status=status,
            duration=duration,
            output=output,
            error=error_msg,
            return_code=return_code,
        )

    def run_all_examples(self) -> bool:
        """Запускает все примеры"""
        self.print_header()
        self.print_environment_info()

        examples = self.get_examples()
        print(f"📋 Найдено примеров для запуска: {len(examples)}")
        print()

        # Запускаем каждый пример
        for script_name, description in examples:
            result = self.run_example(script_name, description)
            self.results.append(result)

        return self.print_summary()

    def print_summary(self) -> bool:
        """Выводит итоговую сводку"""
        total_time = time.time() - self.start_time

        print(f"\n{'=' * 80}")
        print("📊 ИТОГИ ВЫПОЛНЕНИЯ")
        print("=" * 80)

        # Статистика по статусам
        status_counts: Dict[ExampleStatus, int] = {}
        for status in ExampleStatus:
            status_counts[status] = len(
                [r for r in self.results if r.status == status]
            )

        print(f"✅ Успешно: {status_counts.get(ExampleStatus.SUCCESS, 0)}")
        print(f"❌ С ошибками: {status_counts.get(ExampleStatus.FAILED, 0)}")
        print(f"⏭️ Пропущено: {status_counts.get(ExampleStatus.SKIPPED, 0)}")
        print(f"⏱️ Таймаут: {status_counts.get(ExampleStatus.TIMEOUT, 0)}")
        print(
            f"💥 Критические ошибки: {status_counts.get(ExampleStatus.ERROR, 0)}"
        )
        print(f"⏱️ Общее время: {total_time:.2f} сек")

        # Детальная информация по каждому примеру
        print("\n📋 Детальная информация:")
        for result in self.results:
            status_emoji = result.status.value
            duration_str = f"{result.duration:.2f}с"
            print(
                f"   {status_emoji} {result.name} ({duration_str}) - {result.description}"
            )
            if result.error:
                print(f"      💬 {result.error}")

        # Общий результат
        successful: int = status_counts.get(ExampleStatus.SUCCESS, 0)
        total = len(self.results)

        print(
            f"\n🎯 Результат: {successful}/{total} примеров выполнено успешно"
        )

        if successful == total:
            print("🎉 Все примеры выполнены успешно!")
            print("\n💡 Дополнительная информация:")
            print("   📚 Документация: docs/")
            print("   🧪 Тесты: make test")
            print("   🔧 Линтинг: make lint")
            return True
        else:
            print(f"⚠️ {total - successful} примеров завершились с ошибками")
            print("\n💡 Рекомендации:")
            print("   🔑 Проверьте переменные окружения")
            print("   🌐 Убедитесь в доступности API")
            print("   📚 См. документацию для настройки")
            return False


def main() -> int:
    """Главная функция"""
    runner = ExampleRunner()
    success = runner.run_all_examples()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
