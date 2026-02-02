#!/usr/bin/env python3
"""
Скрипт для создания тестовых данных для пагинации
"""
import sys
import os
from pathlib import Path

# Добавляем src в путь Python
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from src.api.items_client import ItemsAPIClient
    from faker import Faker
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("\nУбедитесь, что:")
    print("1. Установлены зависимости: pip install -r requirements.txt")
    print("2. Файл .env настроен правильно")
    print("3. Структура проекта корректна:")
    print("   - create_test_data.py в корне проекта")
    print("   - папка src/ с модулями")
    sys.exit(1)


def create_test_items(count: int = 20):
    """Создание тестовых элементов"""
    print(f"🎯 Создание {count} тестовых элементов...")
    print("=" * 60)

    try:
        client = ItemsAPIClient()
    except Exception as e:
        print(f"❌ Ошибка при создании клиента: {e}")
        print("\n🔧 Возможные причины:")
        print("1. Проверьте файл .env в корне проекта")
        print("2. Убедитесь, что указаны:")
        print("   - BASE_URL=https://api.fast-api.senior-pomidorov.ru")
        print("   - USER_EMAIL=ваш_настоящий_email")
        print("   - USER_PASSWORD=ваш_настоящий_пароль")
        print("3. Проверьте интернет-соединение")
        return

    fake = Faker()

    created_count = 0
    failed_count = 0

    for i in range(count):
        try:
            item_data = {
                "title": f"Test Item {i + 1}: {fake.word().capitalize()}",
                "description": fake.sentence()
            }

            item = client.create_item(item_data)
            created_count += 1
            print(f"✅ [{i + 1:2d}/{count}] Создан элемент ID={item.id:4d}: '{item.title[:40]}...'")

        except Exception as e:
            failed_count += 1
            print(f"❌ [{i + 1:2d}/{count}] Ошибка: {str(e)[:80]}...")
            continue

    print("=" * 60)
    print(f"📊 ИТОГ:")
    print(f"   Успешно создано: {created_count}")
    print(f"   Не удалось создать: {failed_count}")
    print(f"   Всего попыток: {count}")

    # Проверяем общее количество
    try:
        items = client.get_items(size=1)
        print(f"\n📈 Всего элементов в системе: {items.count}")

        if items.count >= 15:
            print("🎉 Достаточно элементов для тестирования пагинации!")
        else:
            print(f"⚠️  Мало элементов ({items.count}) для полноценного тестирования пагинации")
            print("   Создайте еще элементов через UI или запустите скрипт снова")

    except Exception as e:
        print(f"\n⚠️  Ошибка при проверке количества: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Создание тестовых данных для пагинации API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python create_test_data.py          # Создать 20 элементов
  python create_test_data.py -n 30    # Создать 30 элементов
  python create_test_data.py --number 15  # Создать 15 элементов

Для работы скрипта нужен файл .env с настройками:
  BASE_URL=https://api.fast-api.senior-pomidorov.ru
  USER_EMAIL=your_email@example.com
  USER_PASSWORD=your_password
        """
    )

    parser.add_argument(
        "-n", "--number",
        type=int,
        default=20,
        help="Количество элементов для создания (по умолчанию: 20)"
    )

    args = parser.parse_args()
    create_test_items(args.number)