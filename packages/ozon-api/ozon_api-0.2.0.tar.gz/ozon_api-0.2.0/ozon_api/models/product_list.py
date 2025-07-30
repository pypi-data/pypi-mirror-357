from pydantic import BaseModel, Field
from typing import List, Literal


class ProductListFilter(BaseModel):
    offer_id: List[str] | None = Field(None, description="Артикулы товаров (offer_id)")
    product_id: List[int] | None = Field(None, description="ID товаров (product_id)")
    visibility: str | None = Field(
        None, description="Видимость товара (ALL, VISIBLE, INVISIBLE)"
    )
    # Можно добавить другие поля фильтра по необходимости


class ProductListRequest(BaseModel):
    filter: ProductListFilter = Field(..., description="Фильтр товаров")
    last_id: str | None = Field(
        None, description="Идентификатор последнего товара для пагинации"
    )
    limit: int = Field(
        1000, description="Максимальное количество товаров в ответе (1-1000)"
    )
    sort_by: str | None = Field(None, description="Сортировка (например, 'product_id')")
    sort_dir: Literal["ASC", "DESC"] | None = Field(
        None, description="Направление сортировки"
    )


class ProductListItem(BaseModel):
    product_id: int = Field(..., description="ID товара в системе Ozon")
    offer_id: str = Field(..., description="Артикул товара (offer_id)")
    visibility: str = Field(..., description="Видимость товара")
    # Можно добавить другие поля из ответа по необходимости


class ProductListResponse(BaseModel):
    items: List[dict] = Field(..., description="Список товаров")
    total: int = Field(..., description="Общее количество товаров")
    last_id: str | None = Field(
        None, description="Идентификатор последнего товара для пагинации"
    )


class ProductListResult(BaseModel):
    result: ProductListResponse
