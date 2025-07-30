from pydantic import BaseModel, Field
from typing import List


class ProductSubscriptionRequest(BaseModel):
    skus: List[int] = Field(
        ..., description="Список SKU, идентификаторов товара в системе Ozon."
    )


class ProductSubscriptionItem(BaseModel):
    sku: int = Field(..., description="Идентификатор товара в системе Ozon, SKU.")
    count: int = Field(..., description="Количество подписавшихся пользователей.")


class ProductSubscriptionResponse(BaseModel):
    result: List[ProductSubscriptionItem] = Field(
        ..., description="Результат работы метода."
    )
