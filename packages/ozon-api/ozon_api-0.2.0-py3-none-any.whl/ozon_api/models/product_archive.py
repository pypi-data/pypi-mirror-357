from pydantic import BaseModel, Field
from typing import List


class ProductArchiveRequest(BaseModel):
    product_id: List[int | str] = Field(
        ..., description="Список product_id для архивации (до 100)"
    )


class ProductArchiveResponse(BaseModel):
    result: bool = Field(
        ..., description="Результат обработки запроса: true, если успешно"
    )


class ProductUnarchiveRequest(BaseModel):
    product_id: List[int | str] = Field(
        ..., description="Список product_id для разархивации (до 100)"
    )


class ProductUnarchiveResponse(BaseModel):
    result: bool = Field(
        ..., description="Результат обработки запроса: true, если успешно"
    )
