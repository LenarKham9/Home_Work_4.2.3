import requests
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from src.models.schemas import (
    ItemCreate, ItemUpdate, ItemResponse,
    ItemsListResponse, TokenResponse, ErrorResponse
)

load_dotenv()


class ItemsAPIClient:
    """Клиент для работы с Items API"""

    def __init__(self):
        self.base_url = os.getenv("BASE_URL", "https://api.fast-api.senior-pomidorov.ru")
        self.token = self._get_auth_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        print(f"✅ API Client initialized for {self.base_url}")

    def _get_auth_token(self) -> str:
        """Получение токена авторизации"""
        auth_data = {
            "username": os.getenv("USER_EMAIL"),
            "password": os.getenv("USER_PASSWORD")
        }

        print(f"🔐 Getting token for user: {auth_data['username']}")

        response = requests.post(
            f"{self.base_url}/api/v1/login/access-token",
            data=auth_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.status_code != 200:
            raise Exception(f"Auth failed: {response.status_code} - {response.text}")

        token_response = TokenResponse.parse_obj(response.json())
        print("✅ Token received successfully")
        return token_response.access_token

    def create_item(self, item_data: Dict[str, Any]) -> ItemResponse:
        """POST /api/v1/items/ - создание элемента"""
        # Валидация входных данных через Pydantic
        ItemCreate(**item_data)

        print(f"📝 Creating item: {item_data['title'][:30]}...")

        response = requests.post(
            f"{self.base_url}/api/v1/items/",
            json=item_data,
            headers=self.headers
        )

        if response.status_code not in [200, 201]:
            print(f"❌ Create failed: {response.status_code} - {response.text}")
            response.raise_for_status()

        return ItemResponse.parse_obj(response.json())

    def get_items(
            self,
            page: int = 1,
            size: int = 10,
            sort_by: Optional[str] = None,
            order: str = "asc",
            search: Optional[str] = None
    ) -> ItemsListResponse:
        """GET /api/v1/items/ - получение списка элементов"""
        params = {"page": page, "size": size}
        if sort_by:
            params.update({"sort_by": sort_by, "order": order})
        if search:
            params["search"] = search

        print(f"📋 Getting items page {page}, size {size}")

        response = requests.get(
            f"{self.base_url}/api/v1/items/",
            params=params,
            headers=self.headers
        )

        if response.status_code != 200:
            print(f"❌ Get items failed: {response.status_code} - {response.text}")
            response.raise_for_status()

        return ItemsListResponse.parse_obj(response.json())

    def update_item(self, item_id: int, item_data: Dict[str, Any]) -> ItemResponse:
        """PUT /api/v1/items/{id} - полное обновление элемента"""
        # Валидация входных данных через Pydantic
        ItemUpdate(**item_data)

        print(f"🔄 Updating item {item_id}")

        response = requests.put(
            f"{self.base_url}/api/v1/items/{item_id}",
            json=item_data,
            headers=self.headers
        )

        if response.status_code != 200:
            print(f"❌ Update failed: {response.status_code} - {response.text}")
            response.raise_for_status()

        return ItemResponse.parse_obj(response.json())

    def delete_item(self, item_id: str) -> bool:
        """DELETE /api/v1/items/{id} - удаление элемента"""
        print(f"🗑️ Deleting item {item_id}")

        response = requests.delete(
            f"{self.base_url}/api/v1/items/{item_id}",
            headers=self.headers
        )

        if response.status_code == 204:
            print(f"✅ Item {item_id} deleted")
            return True

        if response.status_code != 200:
            print(f"❌ Delete failed: {response.status_code} - {response.text}")
            response.raise_for_status()

        return True

    def get_item_by_id(self, item_id: str) -> ItemResponse:
        """Получение элемента по ID (для проверки)"""
        response = requests.get(
            f"{self.base_url}/api/v1/items/{item_id}",
            headers=self.headers
        )

        if response.status_code != 200:
            print(f"❌ Get item failed: {response.status_code} - {response.text}")
            response.raise_for_status()

        return ItemResponse.parse_obj(response.json())