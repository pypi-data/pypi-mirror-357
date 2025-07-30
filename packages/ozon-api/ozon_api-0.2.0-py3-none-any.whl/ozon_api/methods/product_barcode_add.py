from typing import Type
from ozon_api.base import OzonAPIBase
from ozon_api.models.product_barcode_add import (
    ProductBarcodeAddRequest,
    ProductBarcodeAddResponse,
)


class OzonProductBarcodeAddAPI(OzonAPIBase):
    async def product_barcode_add(
        self: Type["OzonProductBarcodeAddAPI"], request: ProductBarcodeAddRequest
    ) -> ProductBarcodeAddResponse:
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="barcode/add",
            json=request.model_dump(),
        )
        return ProductBarcodeAddResponse(**data)
