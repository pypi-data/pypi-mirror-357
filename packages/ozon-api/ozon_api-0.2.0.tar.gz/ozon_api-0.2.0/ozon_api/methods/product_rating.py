from typing import Type
from ozon_api.base import OzonAPIBase
from ozon_api.models.product_rating import ProductRatingRequest, ProductRatingResponse


class OzonProductRatingAPI(OzonAPIBase):
    async def product_rating_by_sku(
        self: Type["OzonProductRatingAPI"], request: ProductRatingRequest
    ) -> ProductRatingResponse:
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/rating-by-sku",
            json=request.model_dump(),
        )
        return ProductRatingResponse(**data)
