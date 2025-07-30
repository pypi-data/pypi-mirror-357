from typing import Type
from ozon_api.base import OzonAPIBase
from ozon_api.models.product_update_offer_id import (
    ProductUpdateOfferIdRequest,
    ProductUpdateOfferIdResponse,
)


class OzonProductUpdateOfferIdAPI(OzonAPIBase):
    async def product_update_offer_id(
        self: Type["OzonProductUpdateOfferIdAPI"], request: ProductUpdateOfferIdRequest
    ) -> ProductUpdateOfferIdResponse:
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/update/offer-id",
            json=request.model_dump(),
        )
        return ProductUpdateOfferIdResponse(**data)
