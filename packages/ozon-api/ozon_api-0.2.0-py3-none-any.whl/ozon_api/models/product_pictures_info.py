from pydantic import BaseModel, Field
from typing import List


class ProductPicturesInfoRequestV2(BaseModel):
    product_id: List[int] = Field(
        ...,
        description="Список идентификаторов товаров в системе продавца — product_id.",
    )


class ProductPicturesInfoItemV2(BaseModel):
    product_id: int = Field(
        ..., description="Идентификатор товара в системе продавца — product_id."
    )
    primary_photo: List[str] = Field(
        default_factory=list, description="Ссылка на главное изображение."
    )
    photo: List[str] = Field(
        default_factory=list, description="Ссылки на фотографии товара."
    )
    color_photo: List[str] = Field(
        default_factory=list, description="Ссылки на загруженные образцы цвета."
    )
    photo_360: List[str] = Field(
        default_factory=list, description="Ссылки на изображения 360."
    )


class ProductPicturesInfoErrorV2(BaseModel):
    product_id: int = Field(
        ..., description="Идентификатор товара, по которому возникла ошибка."
    )
    error: str = Field(..., description="Описание ошибки.")


class ProductPicturesInfoResponseV2(BaseModel):
    items: List[ProductPicturesInfoItemV2] = Field(
        default_factory=list, description="Изображения товаров."
    )
    errors: List[ProductPicturesInfoErrorV2] | None = Field(
        default_factory=list, description="Список ошибок по изображениям товара."
    )
