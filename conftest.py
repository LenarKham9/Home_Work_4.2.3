import pytest
import allure
import sys
import os
from pathlib import Path
from faker import Faker

# Добавляем корневую директорию в путь Python
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

try:
    from src.api.items_client import ItemsAPIClient
except ImportError:
    print("⚠️  Warning: Could not import ItemsAPIClient. Make sure src/ directory exists.")


@pytest.fixture(scope="session")
def api_client():
    """Фикстура API клиента"""
    print("\n" + "=" * 50)
    print("Setting up API client...")
    client = ItemsAPIClient()
    yield client
    print("\n" + "=" * 50)
    print("API client teardown complete")


@pytest.fixture
def item_data():
    """Фикстура данных для создания элемента"""
    fake = Faker()
    data = {
        "title": fake.sentence(nb_words=3)[:50],
        "description": fake.text(max_nb_chars=200)
    }
    print(f"📦 Generated item data: {data['title'][:30]}...")
    return data


@pytest.fixture
def created_item(api_client, item_data):
    """Фикстура созданного элемента (удаляется после теста)"""
    print(f"\n🛠️ Creating test item...")
    item = api_client.create_item(item_data)
    print(f"✅ Created item ID: {item.id}")

    yield item

    # Очистка после теста
    print(f"\n🧹 Cleaning up item {item.id}...")
    try:
        api_client.delete_item(item.id)
        print(f"✅ Item {item.id} cleaned up")
    except Exception as e:
        print(f"⚠️ Could not delete item {item.id}: {e}")


@pytest.fixture
def unauthorized_session():
    """Неавторизованная сессия (без токена)"""
    import requests
    import os
    from dotenv import load_dotenv

    load_dotenv()

    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })

    return session


# Хуки для Allure
def pytest_runtest_makereport(item, call):
    """Хук для Allure отчетов"""
    if call.when == "call":
        if call.excinfo is not None:
            allure.attach(
                str(call.excinfo.value),
                name="Error",
                attachment_type=allure.attachment_type.TEXT
            )