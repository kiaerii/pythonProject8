"""
1. EmptyFileError - пустой файл
2. FatalError - критическая ошибка (нет доступа)
3. DuplicateIdError - дублирующийся ID
"""

import os
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from app.services.validator import TransactionValidator
from app.core.exceptions import (
    EmptyFileError,
    FatalError,
    DuplicateIdError
)


def create_test_files():
    """Создает тестовые файлы для демонстрации ошибок"""

    print("=" * 60)
    print("СОЗДАНИЕ ТЕСТОВЫХ ФАЙЛОВ ДЛЯ ОШИБОК")
    print("=" * 60)

    # 1. Пустой файл (для EmptyFileError)
    empty_file = Path("data/empty_file.csv")
    empty_file.write_text("", encoding='utf-8')
    print(f" Создан пустой файл: {empty_file}")

    # 2. Файл с дублирующимися ID (для DuplicateIdError)
    duplicate_file = Path("data/duplicate_ids.csv")
    duplicate_file.write_text(
        "id,amount,category,date\n"
        "tx001,100,food,2024-01-01\n"
        "tx002,200,transport,2024-01-02\n"
        "tx001,300,entertainment,2024-01-03\n",  # tx001 повторяется!
        encoding='utf-8'
    )
    print(f" Создан файл с дубликатами ID: {duplicate_file}")

    print("\n")


def test_empty_file_error():
    """Тест 1: EmptyFileError - пустой файл"""
    print("-" * 60)
    print("ТЕСТ 1: EmptyFileError (пустой файл)")
    print("-" * 60)

    from app.io.csv_reader import CSVReader

    empty_file = Path("data/empty_file.csv")

    try:
        reader = CSVReader(empty_file)
        print(" Ошибка не сработала! Файл должен быть пустым.")
    except EmptyFileError as e:
        print(f" УСПЕХ! Поймана ошибка EmptyFileError:")
        print(f"   {e}")
    except Exception as e:
        print(f" Поймана другая ошибка: {type(e).__name__}: {e}")


def test_duplicate_id_error():
    """Тест 2: DuplicateIdError - дублирующийся ID"""
    print("\n" + "-" * 60)
    print("ТЕСТ 2: DuplicateIdError (дублирующийся ID)")
    print("-" * 60)

    from app.io.csv_reader import CSVReader

    duplicate_file = Path("data/duplicate_ids.csv")

    try:
        reader = CSVReader(duplicate_file)
        # Сбрасываем processed_ids для чистого теста
        CSVReader.processed_ids.clear()

        for record in reader.read_records():
            print(f"   Прочитана запись: {record.get('id')}")

        print(" Ошибка не сработала! Должен быть дубликат ID.")
    except DuplicateIdError as e:
        print(f" УСПЕХ! Поймана ошибка DuplicateIdError:")
        print(f"   {e}")
    except Exception as e:
        print(f" Другая ошибка: {type(e).__name__}: {e}")


def test_fatal_error():
    """Тест 3: FatalError - нет доступа к файлу"""
    print("\n" + "-" * 60)
    print("ТЕСТ 3: FatalError (нет доступа к файлу)")
    print("-" * 60)

    from app.io.csv_reader import CSVReader

    # Создаем файл и делаем его доступным только для чтения
    protected_file = Path("data/protected.csv")
    protected_file.write_text("id,amount,category,date\ntest,100,food,2024-01-01", encoding='utf-8')

    # Делаем файл доступным только для чтения (Windows)
    try:
        os.chmod(protected_file, 0o444)  # Только чтение
    except:
        pass

    try:
        reader = CSVReader(protected_file)
        print(" Ошибка не сработала! Файл должен быть защищен.")
    except FatalError as e:
        print(f" УСПЕХ! Поймана ошибка FatalError:")
        print(f"   {e}")
    except Exception as e:
        print(f" Поймана другая ошибка: {type(e).__name__}: {e}")


def run_full_processing():
    """Тест 4: Запуск полной обработки с ошибками"""
    print("\n" + "=" * 60)
    print("ТЕСТ 4: Полная обработка всех файлов")
    print("=" * 60)

    # Запускаем основную программу
    try:
        # Импортируем main и запускаем
        import main
        print("\nЗапуск основной программы...")
        print("(Ожидаем ошибки в файлах empty_file.csv и duplicate_ids.csv)")

    except SystemExit:
        print("\n Программа завершилась с кодом ошибки (как и ожидалось)")
    except Exception as e:
        print(f"\n Неожиданная ошибка: {e}")


def cleanup():
    print("\n" + "=" * 60)
    print("ОЧИСТКА ТЕСТОВЫХ ФАЙЛОВ")
    print("=" * 60)

    test_files = [
        "data/empty_file.csv",
        "data/duplicate_ids.csv",
        "data/protected.csv"
    ]

    for file_path in test_files:
        path = Path(file_path)
        if path.exists():
            try:
                # Снимаем защиту перед удалением
                os.chmod(path, 0o666)
                path.unlink()
                print(f" Удален: {file_path}")
            except Exception as e:
                print(f" Не удалось удалить {file_path}: {e}")


def main():
    """Главная функция тестирования"""

    print("ДЕМОНСТРАЦИЯ ТРЕХ КАСТОМНЫХ ОШИБОК")

    create_test_files()

    test_empty_file_error()
    test_duplicate_id_error()
    test_fatal_error()

    # Полная обработка
    run_full_processing()

    # Очистка
    cleanup()

    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)


if __name__ == "__main__":
    main()