from typing import List
from pydantic import BaseModel


class ProductRatingGroup(BaseModel):
    name: str
    rating: float
    recommendations: List[str] | None = None


class ProductRatingItem(BaseModel):
    sku: int
    rating: float
    groups: List[ProductRatingGroup]


class ProductRatingRequest(BaseModel):
    skus: List[int]


class ProductRatingResponse(BaseModel):
    products: List[ProductRatingItem]
