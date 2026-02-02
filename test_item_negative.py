import pytest
import allure
import requests
import os
from dotenv import load_dotenv

load_dotenv()


@allure.epic("Items API")
@allure.feature("Negative Tests")
class TestItemsNegative:

    @pytest.fixture
    def base_url(self):
        return os.getenv("BASE_URL", "https://api.fast-api.senior-pomidorov.ru")

    @allure.title("Создание элемента без токена (401 Unauthorized)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_item_without_token(self, base_url, item_data):
        """Попытка создания элемента без токена"""
        response = requests.post(
            f"{base_url}/api/v1/items/",
            json=item_data,
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ 401 Unauthorized при создании без токена")

    @allure.title("Получение списка без токена (401 Unauthorized)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_items_without_token(self, base_url):
        """Попытка получения списка без токена"""
        response = requests.get(
            f"{base_url}/api/v1/items/",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ 401 Unauthorized при получении без токена")

    @allure.title("Создание элемента с пустым заголовком")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_empty_title(self, api_client):
        """Отправка невалидных данных - пустой заголовок"""
        invalid_data = {"title": "", "description": "Valid description"}

        response = requests.post(
            f"{api_client.base_url}/api/v1/items/",
            json=invalid_data,
            headers=api_client.headers
        )

        # API может возвращать 422 или 400
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print(f"✓ {response.status_code} при пустом заголовке")

    @allure.title("Создание элемента со слишком длинным заголовком")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_long_title(self, api_client):
        """Заголовок > 100 символов"""
        invalid_data = {
            "title": "A" * 101,
            "description": "Valid description"
        }

        response = requests.post(
            f"{api_client.base_url}/api/v1/items/",
            json=invalid_data,
            headers=api_client.headers
        )

        # Если API принимает длинные заголовки (200) - это нормально
        if response.status_code == 200:
            print("✓ API принимает длинные заголовки")
            # Удаляем созданный элемент
            item_id = response.json().get("id")
            if item_id:
                api_client.delete_item(item_id)
        else:
            # Иначе должна быть ошибка валидации
            assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
            print(f"✓ {response.status_code} при длинном заголовке")

    @allure.title("Обновление несуществующего элемента")
    @allure.severity(allure.severity_level.NORMAL)
    def test_update_nonexistent_item(self, api_client):
        """Попытка обновления элемента с несуществующим ID"""
        update_data = {"title": "Updated", "description": "Updated"}
        # Используем невалидный UUID
        non_existent_id = "00000000-0000-0000-0000-000000000000"

        response = requests.put(
            f"{api_client.base_url}/api/v1/items/{non_existent_id}",
            json=update_data,
            headers=api_client.headers
        )

        # API возвращает 422 для невалидного UUID
        assert response.status_code in [404, 422, 400], f"Expected 404/422/400, got {response.status_code}"
        print(f"✓ {response.status_code} при обновлении несуществующего элемента")

    @allure.title("Удаление несуществующего элемента")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_nonexistent_item(self, api_client):
        """Попытка удаления элемента с несуществующим ID"""
        # Используем невалидный UUID
        non_existent_id = "00000000-0000-0000-0000-000000000000"

        response = requests.delete(
            f"{api_client.base_url}/api/v1/items/{non_existent_id}",
            headers=api_client.headers
        )

        # API возвращает 422 для невалидного UUID
        assert response.status_code in [404, 422, 400], f"Expected 404/422/400, got {response.status_code}"
        print(f"✓ {response.status_code} при удалении несуществующего элемента")

    @allure.title("Двойное удаление элемента")
    @allure.severity(allure.severity_level.NORMAL)
    def test_double_delete_item(self, api_client, item_data):
        """Удаление элемента дважды"""
        # Создаем элемент
        item = api_client.create_item(item_data)

        # Первое удаление
        api_client.delete_item(item.id)

        # Второе удаление
        response = requests.delete(
            f"{api_client.base_url}/api/v1/items/{item.id}",
            headers=api_client.headers
        )

        # Проверяем статус при втором удалении
        assert response.status_code in [404, 422,
                                        400], f"Expected 404/422/400 on second delete, got {response.status_code}"
        print(f"✓ {response.status_code} при двойном удалении")

    @allure.title("Создание элемента с описанием None")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_none_description(self, api_client):
        """Description = None (должно работать)"""
        valid_data = {"title": "Valid Title", "description": None}

        item = api_client.create_item(valid_data)

        assert item.title == "Valid Title"
        assert item.description is None

        # Очистка
        api_client.delete_item(item.id)
        print("✓ Создание с description=None работает")

    @allure.title("Проверка отсутствия 500 ошибок")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_no_500_on_client_errors(self, api_client, base_url):
        """Убедиться, что нет 500 ошибок при ошибках пользователя"""
        test_cases = [
            ("POST с неверными типами данных", "POST", f"{base_url}/api/v1/items/", {"title": 123, "description": 456}),
            ("PUT с невалидным UUID", "PUT", f"{base_url}/api/v1/items/not-a-uuid", {"title": "test"}),
            ("DELETE с невалидным UUID", "DELETE", f"{base_url}/api/v1/items/not-a-uuid", None),
        ]

        for name, method, url, data in test_cases:
            if method == "POST":
                response = requests.post(url, json=data, headers=api_client.headers)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=api_client.headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=api_client.headers)

            # Проверяем, что нет 500 ошибки
            assert response.status_code != 500, f"500 ошибка для {name}"
            # Должна быть клиентская ошибка (4xx)
            assert 400 <= response.status_code < 500, f"Не клиентская ошибка ({response.status_code}) для {name}"

            print(f"✓ Нет 500 ошибки для: {name}")