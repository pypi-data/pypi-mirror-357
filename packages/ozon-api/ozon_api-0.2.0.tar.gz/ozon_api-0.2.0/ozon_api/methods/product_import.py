from typing import Type
from ozon_api.base import OzonAPIBase
from ozon_api.models.product_import import ProductImport
from ozon_api.models.import_by_sku import ImportBySku
from ozon_api.models.product_import_info import ProductImportInfo
from ozon_api.models.product_attributes_update import ProductAttributesUpdate
from ozon_api.models.products_delete import (
    ProductsDeleteRequest,
    ProductsDeleteResponse,
)
from ozon_api.models.upload_digital_codes import (
    UploadDigitalCodesRequest,
    UploadDigitalCodesResponse,
    UploadDigitalCodesInfoRequest,
    UploadDigitalCodesInfoResponse,
)


class OzonProductImportAPI(OzonAPIBase):
    async def product_import(
        self: Type["OzonProductImportAPI"], request: ProductImport
    ) -> dict:
        data = await self._request(
            method="post",
            api_version="v3",
            endpoint="product/import",
            json=request.model_dump(),
        )
        return data

    async def product_import_info(
        self: Type["OzonProductImportAPI"], request: ProductImportInfo
    ) -> dict:
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/import/info",
            json=request.model_dump(),
        )
        return data

    async def product_import_by_sku(
        self: Type["OzonProductImportAPI"], request: ImportBySku
    ) -> dict:
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/import-by-sku",
            json=request.model_dump(),
        )
        return data

    async def product_attributes_update(
        self: Type["OzonProductImportAPI"], request: ProductAttributesUpdate
    ) -> dict:
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/attributes/update",
            json=request.model_dump(),
        )
        return data

    async def products_delete(
        self: Type["OzonProductImportAPI"], request: ProductsDeleteRequest
    ) -> ProductsDeleteResponse:
        data = await self._request(
            method="post",
            api_version="v2",
            endpoint="products/delete",
            json=request.model_dump(),
        )
        return ProductsDeleteResponse(**data)

    async def upload_digital_codes(
        self: Type["OzonProductImportAPI"], request: UploadDigitalCodesRequest
    ) -> UploadDigitalCodesResponse:
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/upload_digital_codes",
            json=request.model_dump(),
        )
        return UploadDigitalCodesResponse(**data)

    async def upload_digital_codes_info(
        self: Type["OzonProductImportAPI"], request: UploadDigitalCodesInfoRequest
    ) -> UploadDigitalCodesInfoResponse:
        data = await self._request(
            method="post",
            api_version="v1",
            endpoint="product/upload_digital_codes/info",
            json=request.model_dump(),
        )
        return UploadDigitalCodesInfoResponse(**data)
