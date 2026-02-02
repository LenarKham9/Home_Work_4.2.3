from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime


class ItemCreate(BaseModel):
    """Модель для создания элемента"""
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ItemUpdate(BaseModel):
    """Модель для обновления элемента"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ItemResponse(BaseModel):
    """Модель ответа для элемента (реальный API)"""
    id: str  # UUID как строка
    title: str
    description: Optional[str]
    owner_id: str  # Добавляем owner_id
    created_at: Optional[datetime] = None  # Может быть None
    updated_at: Optional[datetime] = None  # Может быть None


class ItemsListResponse(BaseModel):
    """Модель ответа для списка элементов (реальный API без пагинации)"""
    data: List[ItemResponse]
    count: int
    # API не возвращает поля пагинации, делаем их опциональными
    page: Optional[int] = None
    total_pages: Optional[int] = None
    has_next: Optional[bool] = None
    has_prev: Optional[bool] = None


class ErrorResponse(BaseModel):
    """Модель ответа при ошибке"""
    detail: Union[str, List[dict]]


class TokenResponse(BaseModel):
    """Модель ответа с токеном"""
    access_token: str
    token_type: str = "bearer"