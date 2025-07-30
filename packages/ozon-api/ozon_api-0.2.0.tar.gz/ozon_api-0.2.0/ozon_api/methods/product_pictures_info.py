from typing import Type
from ozon_api.base import OzonAPIBase
from ozon_api.models.product_pictures_info import (
    ProductPicturesInfoRequestV2,
    ProductPicturesInfoResponseV2,
)


class OzonProductPicturesInfoAPI(OzonAPIBase):
    async def product_pictures_info_v2(
        self: Type["OzonProductPicturesInfoAPI"], request: ProductPicturesInfoRequestV2
    ) -> ProductPicturesInfoResponseV2:
        data = await self._request(
            method="post",
            api_version="v2",
            endpoint="product/pictures/info",
            json=request.model_dump(),
        )
        return ProductPicturesInfoResponseV2(**data)
