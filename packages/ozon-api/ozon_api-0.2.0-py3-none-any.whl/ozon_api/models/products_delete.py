from pydantic import BaseModel, Field
from typing import List


class ProductDeleteItem(BaseModel):
    product_id: str = Field(
        ..., description="Идентификатор товара в системе продавца — product_id."
    )


class ProductsDeleteRequest(BaseModel):
    products: List[ProductDeleteItem] = Field(
        ..., description="Список товаров для удаления (до 500)"
    )


class ProductsDeleteStatusItem(BaseModel):
    error: str | None = Field(None, description="Причина ошибки, если возникла")
    is_deleted: bool = Field(
        ..., description="Если запрос выполнен без ошибок и товары удалены — true."
    )
    offer_id: str = Field(
        ..., description="Идентификатор товара в системе продавца — артикул."
    )


class ProductsDeleteResponse(BaseModel):
    status: List[ProductsDeleteStatusItem] = Field(
        ..., description="Статус обработки запроса."
    )
