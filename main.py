#!/usr/bin/env python3
"""
Data Integration Engine - система агрегации финансовых отчетов.
"""

import sys
import argparse
import logging
from pathlib import Path

from app.io import ReaderRegistry
from app.services.validator import TransactionValidator
from app.services.aggregator import TransactionAggregator
from app.core.exceptions import FatalError, DataFormatError


def setup_logging(log_file: Path = Path("../../Desktop/app.log")) -> None:
    """Настройка логирования."""
    log_file_path = Path(log_file)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()

    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


def process_directory(
    data_dir: Path,
    output_path: Path,
    strict_duplicates: bool = True
) -> dict:
    """Обрабатывает все файлы в директории."""
    logger = logging.getLogger(__name__)

    if not data_dir.exists():
        raise FatalError(f"Директория не существует: {data_dir}")

    if not data_dir.is_dir():
        raise FatalError(f"Путь не является директорией: {data_dir}")

    validator = TransactionValidator()
    aggregator = TransactionAggregator()

    files_processed = 0
    files_failed = 0
    errors_by_file = {}

    all_files = list(data_dir.glob("*"))
    logger.info(f"Начинаем обработку {len(all_files)} файлов в {data_dir}")

    for file_path in all_files:
        if not file_path.is_file():
            continue

        logger.info(f"Обработка файла: {file_path.name}")

        try:
            reader = ReaderRegistry.get_reader(file_path)
            if reader is None:
                logger.warning(
                    f"Пропуск файла: {file_path.name}"
                    f"(неподдерживаемый формат)"
                )
                files_failed += 1
                errors_by_file[file_path.name] = [
                    "Неподдерживаемый формат файла"
                ]
                continue

            file_errors = []
            records_processed = 0

            for raw_record in reader.read_records():
                transaction = validator.validate_and_create_transaction(
                    raw_data=raw_record,
                    file_name=file_path.name,
                    strict_duplicates=strict_duplicates
                )

                if transaction:
                    aggregator.add_transaction(transaction)
                    records_processed += 1
                else:
                    record_id = raw_record.get('id', 'unknown')
                    file_errors.append(
                        f"Запись {record_id}: ошибка валидации"
                    )

            files_processed += 1

            if file_errors:
                errors_by_file[file_path.name] = file_errors
                logger.warning(
                    f"Файл {file_path.name} обработан с {len(file_errors)} "
                    f"ошибками. Успешных записей: {records_processed}"
                )
            else:
                logger.info(
                    f"Файл {file_path.name} обработан успешно. "
                    f"Записей: {records_processed}"
                )

        except DataFormatError as e:
            files_failed += 1
            errors_by_file[file_path.name] = [str(e)]
            logger.error(f"Ошибка формата в файле {file_path.name}: {e}")

        except Exception as e:
            files_failed += 1
            errors_by_file[file_path.name] = [f"Неожиданная ошибка: {e}"]
            logger.exception(
                f"Критическая ошибка при обработке {file_path.name}"
            )

    # Проверяем консистентность валют
    for category, transactions in aggregator.transactions.items():
        currencies = set(t.currency for t in transactions)
        if len(currencies) > 1:
            logger.warning(
                f"Категория '{category}' содержит транзакции "
                f"в разных валютах: {currencies}"
            )

    # Экспортируем результат
    try:
        aggregator.export_to_json(output_path, atomic_write=True)
    except Exception as e:
        logger.error(f"Ошибка при экспорте результата: {e}")
        raise

    # Собираем статистику
    stats = {
        "total_files": len(all_files),
        "processed_successfully": files_processed,
        "failed": files_failed,
        "total_errors": len(validator.errors),
        "total_transactions": sum(
            len(txs) for txs in aggregator.transactions.values()
        ),
        "errors_by_file": errors_by_file,
        "validation_errors": [
            {
                "file": err.file_name,
                "record": err.record_id,
                "type": err.error_type,
                "message": err.error_message
            }
            for err in validator.errors
        ]
    }

    return stats


def print_report(stats: dict) -> None:
    """Выводит отчет о обработке в консоль."""
    print("\n" + "=" * 60)
    print("ОТЧЕТ ОБ ОБРАБОТКЕ ДАННЫХ")
    print("=" * 60)
    print(f"Всего файлов: {stats['total_files']}")
    print(f"Успешно обработано: {stats['processed_successfully']}")
    print(f"С ошибками: {stats['failed']}")
    print(f"Всего транзакций: {stats['total_transactions']}")
    print(f"Всего ошибок валидации: {stats['total_errors']}")

    if stats['validation_errors']:
        print("\n" + "-" * 60)
        print("СПИСОК ОШИБОК ВАЛИДАЦИИ:")
        print("-" * 60)
        for err in stats['validation_errors'][:10]:
            print(f"  Файл: {err['file']}")
            if err['record']:
                print(f"  Запись: {err['record']}")
            print(f"  Тип: {err['type']}")
            print(f"  Сообщение: {err['message']}")
            print()

    if stats['errors_by_file']:
        print("\n" + "-" * 60)
        print("ОШИБКИ ПО ФАЙЛАМ:")
        print("-" * 60)
        for filename, errors in stats['errors_by_file'].items():
            print(f"\n  {filename}:")
            for error in errors[:3]:
                print(f"    - {error}")

    print("\n" + "=" * 60)


def main() -> None:
    """Главная функция."""
    parser = argparse.ArgumentParser(
        description="Data Integration Engine - агрегация финансовых отчетов"
    )
    parser.add_argument(
        'data_dir',
        type=str,
        nargs='?',
        default='data',
        help='Директория с входными файлами (по умолчанию: data)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='result.json',
        help='Путь к выходному файлу (по умолчанию: result.json)'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        default='app.log',
        help='Путь к файлу лога (по умолчанию: app.log)'
    )
    parser.add_argument(
        '--no-atomic',
        action='store_true',
        help='Отключить атомарную запись'
    )

    args = parser.parse_args()

    # Настройка логирования
    setup_logging(args.log_file)
    logger = logging.getLogger(__name__)

    logger.info("Запуск Data Integration Engine")

    try:
        # Обработка данных
        stats = process_directory(
            data_dir=Path(args.data_dir),
            output_path=Path(args.output),
            strict_duplicates=True
        )

        # Вывод отчета
        print_report(stats)

        # Логируем результат
        logger.info(
            f"Обработка завершена. Успешно:"
            f"{stats['processed_successfully']}, "
            f"Ошибок: {stats['failed']}, "
            f"Транзакций: {stats['total_transactions']}"
        )

        # Код возврата
        if stats['failed'] > 0:
            sys.exit(1)
        sys.exit(0)

    except FatalError as e:
        logger.critical(f"Фатальная ошибка: {e}")
        print(f"\nОШИБКА: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Обработка прервана пользователем")
        sys.exit(130)
    except Exception as e:
        logger.exception("Необработанная ошибка")
        print(f"\nНЕОЖИДАННАЯ ОШИБКА: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
