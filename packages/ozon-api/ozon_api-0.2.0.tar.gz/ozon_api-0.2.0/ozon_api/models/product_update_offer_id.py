from pydantic import BaseModel, Field
from typing import List


class ProductUpdateOfferIdItem(BaseModel):
    offer_id: str = Field(..., description="Старый артикул (offer_id)")
    new_offer_id: str = Field(..., description="Новый артикул (new_offer_id)")


class ProductUpdateOfferIdRequest(BaseModel):
    update_offer_id: List[ProductUpdateOfferIdItem] = Field(
        ..., description="Список пар старый/новый артикул"
    )


class ProductUpdateOfferIdError(BaseModel):
    offer_id: str = Field(..., description="Артикул, который не удалось изменить")
    message: str = Field(..., description="Сообщение об ошибке")


class ProductUpdateOfferIdResponse(BaseModel):
    errors: List[ProductUpdateOfferIdError] = Field(
        default_factory=list, description="Ошибки изменения offer_id"
    )
