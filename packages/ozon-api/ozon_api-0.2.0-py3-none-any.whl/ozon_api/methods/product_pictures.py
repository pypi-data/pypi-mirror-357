from typing import Any, Type
from ozon_api.base import OzonAPIBase


class OzonProductPicturesAPI(OzonAPIBase):
    async def product_pictures_import(
        self: Type["OzonProductPicturesAPI"], items: dict
    ) -> dict[str, Any]:
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/pictures/import",
            json=items,
        )
        return data

    async def product_pictures_info(
        self: Type["OzonProductPicturesAPI"], product_id: list[str]
    ) -> dict[str, Any]:
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/pictures/info",
            json={"product_id": product_id},
        )
        return data
