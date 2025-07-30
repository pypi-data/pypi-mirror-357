from typing import List
from pydantic import BaseModel, ConfigDict


class CategoryTreeItem(BaseModel):
    description_category_id: int | None = None
    category_name: str | None = None
    children: List["CategoryTreeItem"] | None = None
    disabled: bool
    type_id: int | None = None
    type_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


CategoryTreeItem.model_rebuild()


class CategoryTreeResponse(BaseModel):
    result: List[CategoryTreeItem]
