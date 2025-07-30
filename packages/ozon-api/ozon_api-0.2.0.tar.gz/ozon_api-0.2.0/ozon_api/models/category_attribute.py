from typing import List
from pydantic import BaseModel, ConfigDict


class CategoryAttributeItem(BaseModel):
    category_dependent: bool | None = None
    description: str | None = None
    dictionary_id: int | None = None
    group_id: int | None = None
    group_name: str | None = None
    id: int
    is_aspect: bool | None = None
    is_collection: bool | None = None
    is_required: bool | None = None
    name: str
    type: str
    attribute_complex_id: int | None = None
    max_value_count: int | None = None
    complex_is_collection: bool | None = None

    model_config = ConfigDict(from_attributes=True)


class CategoryAttributeResponse(BaseModel):
    result: List[CategoryAttributeItem]
