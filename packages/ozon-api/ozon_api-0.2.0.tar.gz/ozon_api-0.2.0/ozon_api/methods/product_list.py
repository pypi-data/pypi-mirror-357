from typing import Type
from ozon_api.base import OzonAPIBase
from ozon_api.models.product_list import ProductListRequest, ProductListResult


class OzonProductListAPI(OzonAPIBase):
    async def product_list(
        self: Type["OzonProductListAPI"], request: ProductListRequest
    ) -> ProductListResult:
        data = await self._request(
            method="post",
            api_version="v3",
            endpoint="product/list",
            json=request.model_dump(),
        )
        return ProductListResult(**data)

    async def product_info_limit(self: Type["OzonProductListAPI"]) -> dict[str, any]:
        data = await self._request(
            method="post",
            api_version="v4",
            endpoint="product/info/limit",
        )
        return data
