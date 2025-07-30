from typing import Type
from ozon_api.base import OzonAPIBase
from ozon_api.models.product_archive import (
    ProductArchiveRequest,
    ProductArchiveResponse,
    ProductUnarchiveRequest,
    ProductUnarchiveResponse,
)


class OzonProductArchiveAPI(OzonAPIBase):
    async def product_archive(
        self: Type["OzonProductArchiveAPI"], request: ProductArchiveRequest
    ) -> ProductArchiveResponse:
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/archive",
            json=request.model_dump(),
        )
        return ProductArchiveResponse(**data)

    async def product_unarchive(
        self: Type["OzonProductArchiveAPI"], request: ProductUnarchiveRequest
    ) -> ProductUnarchiveResponse:
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/unarchive",
            json=request.model_dump(),
        )
        return ProductUnarchiveResponse(**data)
