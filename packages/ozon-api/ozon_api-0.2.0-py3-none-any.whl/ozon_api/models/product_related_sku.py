from pydantic import BaseModel, Field
from typing import List


class ProductRelatedSkuRequest(BaseModel):
    sku: List[int] = Field(..., description="Список SKU.")


class ProductRelatedSkuItem(BaseModel):
    sku: int = Field(..., description="SKU, связанный с переданными.")
    related_sku: List[int] = Field(..., description="Связанные SKU.")


class ProductRelatedSkuError(BaseModel):
    sku: int = Field(..., description="SKU, по которому возникла ошибка.")
    error: str = Field(..., description="Описание ошибки.")


class ProductRelatedSkuResponse(BaseModel):
    items: List[ProductRelatedSkuItem] = Field(
        default_factory=list, description="Информация о связанных SKU."
    )
    errors: List[ProductRelatedSkuError] | None = Field(
        default_factory=list, description="Ошибки."
    )
