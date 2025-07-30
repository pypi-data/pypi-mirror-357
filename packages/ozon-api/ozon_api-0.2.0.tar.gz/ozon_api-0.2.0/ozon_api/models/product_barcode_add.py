from pydantic import BaseModel, Field
from typing import List


class ProductBarcodeAddItem(BaseModel):
    sku: int = Field(..., description="Идентификатор товара (SKU)")
    barcode: str = Field(..., description="Штрихкод для привязки")


class ProductBarcodeAddRequest(BaseModel):
    barcodes: List[ProductBarcodeAddItem] = Field(
        ..., description="Список штрихкодов и товаров"
    )


class ProductBarcodeAddError(BaseModel):
    code: str = Field(..., description="Код ошибки")
    error: str = Field(..., description="Описание ошибки")
    barcode: str = Field(..., description="Штрихкод, который не удалось привязать")
    sku: int = Field(
        ...,
        description="Идентификатор товара, к которому не удалось привязать штрихкод",
    )


class ProductBarcodeAddResponse(BaseModel):
    errors: List[ProductBarcodeAddError] | None = Field(
        default_factory=list, description="Список ошибок"
    )
