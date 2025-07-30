from pydantic import BaseModel, Field
from typing import List


class UploadDigitalCodesRequest(BaseModel):
    digital_codes: List[str] = Field(..., description="Цифровые коды активации.")
    product_id: int = Field(
        ..., description="Идентификатор товара в системе продавца — product_id."
    )


class UploadDigitalCodesResponseResult(BaseModel):
    task_id: int = Field(..., description="Код задачи на загрузку кодов.")


class UploadDigitalCodesResponse(BaseModel):
    result: UploadDigitalCodesResponseResult = Field(
        ..., description="Результат запроса."
    )


class UploadDigitalCodesInfoRequest(BaseModel):
    task_id: int = Field(
        ..., description="Идентификатор задачи на загрузку кодов активации."
    )


class UploadDigitalCodesInfoResponseResult(BaseModel):
    status: str = Field(..., description="Статус загрузки: pending, imported, failed.")


class UploadDigitalCodesInfoResponse(BaseModel):
    result: UploadDigitalCodesInfoResponseResult = Field(
        ..., description="Результат запроса."
    )
