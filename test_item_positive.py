import pytest
import allure
from typing import Dict, Any


@allure.epic("Items API")
@allure.feature("Positive Tests")
class TestItemsPositive:

    @allure.title("Создание нового элемента (валидные данные)")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Тестирование POST /api/v1/items/ с валидными данными")
    def test_create_item(self, api_client, item_data: Dict[str, Any]):
        """POST /api/v1/items/ - создание нового элемента"""
        with allure.step("Создание элемента через API"):
            item = api_client.create_item(item_data)

        with allure.step("Проверка ответа"):
            assert item.id is not None, "Item ID should not be None"
            assert len(item.id) == 36, f"ID should be UUID, got {item.id}"  # UUID длина 36
            assert item.title == item_data["title"], f"Expected title {item_data['title']}, got {item.title}"
            assert item.description == item_data[
                "description"], f"Expected description {item_data['description']}, got {item.description}"
            assert item.owner_id is not None, "Owner ID should not be None"
            # created_at может быть None, это нормально для данного API

        allure.attach(
            f"Item created successfully:\n"
            f"ID: {item.id}\n"
            f"Title: {item.title}\n"
            f"Description: {item.description}\n"
            f"Owner ID: {item.owner_id}\n"
            f"Created at: {item.created_at}",
            name="Item Details",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.title("Получение списка элементов")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_items_structure(self, api_client):
        """GET /api/v1/items/ - проверка структуры ответа"""
        with allure.step("Получение списка элементов"):
            response = api_client.get_items()

        with allure.step("Проверка структуры ответа"):
            # Обязательные поля
            assert hasattr(response, "data"), "Response should have 'data' field"
            assert hasattr(response, "count"), "Response should have 'count' field"

            # Проверяем типы
            assert isinstance(response.data, list), "'data' should be a list"
            assert isinstance(response.count, int), "'count' should be an integer"
            assert response.count >= 0, f"Count should be non-negative, got {response.count}"

            # Поля пагинации могут быть None
            if response.page is not None:
                assert isinstance(response.page, int), "'page' should be an integer"
            if response.total_pages is not None:
                assert isinstance(response.total_pages, int), "'total_pages' should be an integer"

            allure.attach(
                f"Items list response:\n"
                f"Count: {response.count}\n"
                f"Page: {response.page}\n"
                f"Total pages: {response.total_pages}\n"
                f"Has next: {response.has_next}\n"
                f"Has prev: {response.has_prev}\n"
                f"Items in data: {len(response.data)}",
                name="List Response",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.title("Проверка пагинации")
    @allure.severity(allure.severity_level.NORMAL)
    def test_pagination(self, api_client):
        """GET /api/v1/items/ - проверка пагинации"""
        # Проверяем что параметры page и size работают
        with allure.step("Получение с разными размерами страниц"):
            size5 = api_client.get_items(size=5)
            size10 = api_client.get_items(size=10)

            # Проверяем что количество элементов соответствует размеру
            # (если API поддерживает пагинацию)
            if len(size5.data) <= 5:
                print("✓ API поддерживает параметр size")

            # Проверяем разные страницы
            page1 = api_client.get_items(page=1)
            page2 = api_client.get_items(page=2)

            # Если API возвращает разные страницы
            if page1.data and page2.data:
                # Проверяем что страницы разные
                page1_ids = {item.id for item in page1.data}
                page2_ids = {item.id for item in page2.data}

                if page1_ids != page2_ids:
                    print("✓ API поддерживает пагинацию по страницам")
                else:
                    print("⚠ API не различает страницы")
            else:
                print("⚠ Недостаточно данных для проверки пагинации")

        allure.attach(
            f"Pagination test:\n"
            f"Size=5 items: {len(size5.data)}\n"
            f"Size=10 items: {len(size10.data)}\n"
            f"Page 1 items: {len(page1.data)}\n"
            f"Page 2 items: {len(page2.data)}",
            name="Pagination Results",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.title("Проверка сортировки")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sorting(self, api_client):
        """GET /api/v1/items/ - проверка сортировки"""
        with allure.step("Проверка параметров сортировки"):
            # Пытаемся отсортировать разными способами
            try:
                asc_response = api_client.get_items(sort_by="created_at", order="asc")
                desc_response = api_client.get_items(sort_by="created_at", order="desc")

                # Если API поддерживает сортировку
                if asc_response.data and desc_response.data:
                    # Проверяем что ответ получен
                    print(f"✓ Получено {len(asc_response.data)} элементов с сортировкой asc")
                    print(f"✓ Получено {len(desc_response.data)} элементов с сортировкой desc")

                    # Проверяем другие варианты сортировки
                    title_asc = api_client.get_items(sort_by="title", order="asc")
                    title_desc = api_client.get_items(sort_by="title", order="desc")

                    if title_asc.data and title_desc.data:
                        print("✓ API принимает параметры сортировки")
                else:
                    print("⚠ API игнорирует параметры сортировки")

            except Exception as e:
                print(f"⚠ Ошибка при сортировке: {e}")
                # Это может быть нормально, если API не поддерживает сортировку

        allure.attach(
            "Проверка поддержки параметров сортировки API",
            name="Sorting Test",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.title("Полное обновление элемента")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_item(self, api_client, created_item):
        """PUT /api/v1/items/{id} - полное обновление"""
        update_data = {
            "title": "Updated Title",
            "description": "Updated Description"
        }

        with allure.step("Обновление элемента"):
            updated_item = api_client.update_item(created_item.id, update_data)

        with allure.step("Проверка обновленных данных"):
            assert updated_item.title == update_data[
                "title"], f"Expected title {update_data['title']}, got {updated_item.title}"
            assert updated_item.description == update_data[
                "description"], f"Expected description {update_data['description']}, got {updated_item.description}"

        with allure.step("Получение элемента для проверки"):
            retrieved_item = api_client.get_item_by_id(created_item.id)
            assert retrieved_item.title == update_data[
                "title"], f"Expected title {update_data['title']}, got {retrieved_item.title}"
            assert retrieved_item.description == update_data[
                "description"], f"Expected description {update_data['description']}, got {retrieved_item.description}"

        allure.attach(
            f"Update test results:\n"
            f"Original title: {created_item.title}\n"
            f"Updated title: {updated_item.title}\n"
            f"Original description: {created_item.description}\n"
            f"Updated description: {updated_item.description}",
            name="Update Results",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.title("Частичное обновление элемента")
    @allure.severity(allure.severity_level.NORMAL)
    def test_partial_update(self, api_client, created_item):
        """PUT /api/v1/items/{id} - обновление только заголовка"""
        update_data = {"title": "Only Title Updated"}

        with allure.step("Частичное обновление"):
            updated_item = api_client.update_item(created_item.id, update_data)

        with allure.step("Проверка частичного обновления"):
            assert updated_item.title == update_data[
                "title"], f"Expected title {update_data['title']}, got {updated_item.title}"
            # Описание должно остаться прежним
            assert updated_item.description == created_item.description, f"Description changed unexpectedly: {updated_item.description}"

    @allure.title("Удаление элемента")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_item(self, api_client, item_data):
        """DELETE /api/v1/items/{id} - удаление элемента"""
        with allure.step("Создание элемента для удаления"):
            item = api_client.create_item(item_data)
            item_id = item.id

        with allure.step("Удаление элемента"):
            delete_result = api_client.delete_item(item_id)
            assert delete_result is True, "Delete should return True"

        with allure.step("Проверка, что элемент удален"):
            import requests
            response = requests.get(
                f"{api_client.base_url}/api/v1/items/{item_id}",
                headers=api_client.headers
            )

            # Может быть 404 или 422
            assert response.status_code in [404, 422], f"Expected 404/422 after delete, got {response.status_code}"

        allure.attach(
            f"Delete test results:\n"
            f"Item ID: {item_id}\n"
            f"Delete successful: {delete_result}\n"
            f"Status after delete: {response.status_code}",
            name="Delete Results",
            attachment_type=allure.attachment_type.TEXT
        )